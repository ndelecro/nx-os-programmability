#! /isan/bin/python

import signal
import datetime
import time
import threading
import sys
import os
import json
import re
import urllib2
from pprint import pprint
# To gain access to Cisco NX-OS Infra SDK
import nx_sdk_py

# Global variables
cliP                = 0
sdk                 = 0
event_hdlr          = True
bw_threshold        = 10000000000
intf_list           = []
# In seconds
DELAY_BETWEEN_CHECK = 5

def get_prefix_ifname(prefix):
    global cliP

    print("get_prefix_ifname(%s)" % (str(prefix)))
    show_cmd = "show ip route %s " % (str(prefix))
    print(show_cmd)
    resp_json = json.loads(cliP.execShowCmd(show_cmd, nx_sdk_py.R_JSON))
    print(json.dumps(resp_json))
    try:
        row_prefix = resp_json["TABLE_vrf"]["ROW_vrf"]["TABLE_addrf"]["ROW_addrf"]["TABLE_prefix"]["ROW_prefix"]
    except KeyError:
        return ""
    if (int(row_prefix["ucast-nhops"]) != 1):
        print("ucast-nhops != 1, returning")
        return ""    
    try:
        ifname = row_prefix["TABLE_path"]["ROW_path"]["ifname"]
    except KeyError:
        return ""
    print(ifname)
    return ifname

def find_ecmp_intf():
    global cliP, intf_list
    found = False

    show_cmd = "show ip route"
    resp_json = json.loads(cliP.execShowCmd(show_cmd, nx_sdk_py.R_JSON))
    resp_base = resp_json["TABLE_vrf"]["ROW_vrf"]["TABLE_addrf"]["ROW_addrf"]["TABLE_prefix"]["ROW_prefix"]
    for prefix in resp_base:
        print prefix["ipprefix"]
        print prefix["ucast-nhops"]
        if (int(prefix["ucast-nhops"]) > 1):
            prefix_ecmp = prefix["ipprefix"]
            for nexthop in prefix["TABLE_path"]["ROW_path"]:
                intf = get_prefix_ifname(nexthop["ipnexthop"])
                if (intf != ""):
                    intf_list.append(intf)
            found = True
            break
    print intf_list
    if (found):
        syslog_str = "[%s] Found an ECMP bundle: %s --> %s" % \
                          (sdk.getAppName(), prefix_ecmp, ', '.join(map(str, intf_list)))
        print(syslog_str)
        t = sdk.getTracer()
        t.event(str(syslog_str))

def check_intf_load(intf):
    global cliP, sdk

    t = sdk.getTracer()
    print("check_intf_load()")

    show_cmd = "show interface %s" % (str(intf))
    resp_json = json.loads(cliP.execShowCmd(show_cmd, nx_sdk_py.R_JSON))
    # if there's no entries, exit
    if ("TABLE_interface" not in resp_json):
        return

    out_rate = resp_json["TABLE_interface"]["ROW_interface"]["eth_outrate1_bits"]
    print out_rate
    if (int(out_rate) > bw_threshold):
        syslog_str = "[%s] High egress bandwidth: int=%s, bw=%s" % \
                      (sdk.getAppName(), intf, out_rate)
        t.syslog(t.WARNING, str(syslog_str))

def get_telemetry_json():
    fields = ["interface", "eth_outrate1_bits"]

    for intf in intf_list:
        show_cmd = "show interface %s" % (str(intf))
        resp_json = json.loads(cliP.execShowCmd(show_cmd, nx_sdk_py.R_JSON))
        if ("TABLE_interface" not in resp_json):
            continue
        resp_base = resp_json["TABLE_interface"]["ROW_interface"]
        out_rate = int(resp_base["eth_outrate1_bits"])
        if (out_rate <= bw_threshold):
            continue
        tel_json = {}
        for f in fields:
            tel_json[f] = resp_base[f]
        return tel_json
    return "{}"

class pyCmdHandler(nx_sdk_py.NxCmdHandler):
        def postCliCb(self,clicmd):
                global cliP, pattern_path_dict, bw_threshold

                if clicmd.isKeywordSet("tm-use-only"):
                    print "tm-use"
                    tel_json = get_telemetry_json()
                    clicmd.printConsole(json.dumps(tel_json))

                if "set_bw_threshold_cmd" in clicmd.getCmdName():
                   if "no" in clicmd.getCmdLineStr():
                       print "delete cmd"
                       bw_threshold = 10000000000
                   else:
                       print "add cmd"
                       # Create Int Pointer to get the integer Value
                       int_p = nx_sdk_py.new_intp()
                       int_p = nx_sdk_py.void_to_int(clicmd.getParamValue("<bw-threshold-value>"))
                       # Get the value of int * in python
                       if int_p:
                           bw_threshold = int(nx_sdk_py.intp_value(int_p)) * 1000000
                       print bw_threshold
                return True

def timerThread(name,val):
    global cliP, sdk

    while True:
        if sdk and cliP:
           print "timer kicked - sdk"
           for intf in intf_list:
               check_intf_load(intf)
        else:
           print "timer ticked - not sdk"
        time.sleep(DELAY_BETWEEN_CHECK)

# Perform the event handling loop in a dedicated Python thread.
# All SDK related activities happen here, while the main thread
# may continue to do other work.  The call to startEventLoop will
# block until we break out of it by calling stopEventLoop on
def evtThread(name,val):
    global cliP, sdk, event_hdlr

    sdk = nx_sdk_py.NxSdk.getSdkInst(len(sys.argv), sys.argv)
    if not sdk:
        return

    sdk.setAppDesc('ECMP Monitoring')

    t = sdk.getTracer()
    t.event("[%s] Started service" % sdk.getAppName())

    cliP = sdk.getCliParser()

    nxcmd = cliP.newConfigCmd("set_bw_threshold_cmd", \
        "bw-threshold <bw-threshold-value>")
    nxcmd.updateKeyword("bw-threshold", "Bandwidth threshold for monitoring")
    nxcmd.updateParam("<bw-threshold-value>", \
        "Bandwidth threshold value in Mbps", \
        nx_sdk_py.P_INTEGER)

    nxcmd = cliP.newShowCmd("show_ecmp_monitoring_cmd", "tm-use-only")
    nxcmd.updateKeyword("tm-use-only", "To be used strictly in telemetry configs only")

    # Define our application callback for this new command
    mycmd = pyCmdHandler()
    cliP.setCmdHandler(mycmd)

    # Install the new commands to the NXOS parse tree
    # t.event("Adding commands to CLIS parse tree")
    cliP.addToParseTree()

    find_ecmp_intf()

    # Block in the event loop to service NXOS messages
    print("Starting event loop, CTRL-C to interrupt")
    sdk.startEventLoop()

    # Got here by calling stopEventLoop from signal handler
    t.event("Service Quitting...!")
    event_hdlr = False

    # [Required] Needed for graceful exit.
    nx_sdk_py.NxSdk.__swig_destroy__(sdk)

# Create a timer thread
timer_thread = threading.Thread(target=timerThread, args=("timerThread",0))
timer_thread.daemon = True

# Create a Event Thread to register with NxSDK, CLI Parser, Tracer
# and Start Event loop to keep the application running.
# NOTE: Doesnt need a special Event Thread can be done on Main too.
evt_thread = threading.Thread(target=evtThread, args=("evtThread",0))

evt_thread.start()
timer_thread.start()
evt_thread.join()


