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
cliP                            = 0
sdk                             = 0
event_hdlr                      = True
previous_intf_pdus_rcvd_dict    = {}
# in seconds
check_interval                  = 5
# in packets
storm_limit                     = 3
mycmd                           = 0

def shutdown_interface(intf):
    file = open("/tmp/nxsdk_cmd", "w")
    file.write("int %s\n" % intf)
    file.write("shut\n")
    file.close()
    os.system("cat /tmp/nxsdk_cmd")
    cliP.execConfigCmd("/tmp/nxsdk_cmd")

def check_port_channel(pc):
    global previous_intf_pdus_rcvd_dict, storm_limit, check_interval, sdk

    t = sdk.getTracer()

    # If just one interface, make it a list.  If not, it's already a list of interfaces.
    # Ideally NX-OS would always return a list in the CLI JSON output.
    if (type(pc["TABLE_member"]["ROW_member"]) is not list):
        intf_list = [pc["TABLE_member"]["ROW_member"]]
    else:
        intf_list = pc["TABLE_member"]["ROW_member"]

    for intf in intf_list:
        port = intf["port"]
        pdus_rcvd = int(intf["pdus-rcvd"])

        # First time we see this interface? Save the PDU recv count, and go to the next interface.
        if (port not in previous_intf_pdus_rcvd_dict):
            previous_intf_pdus_rcvd_dict[port] = pdus_rcvd
            continue

        # Get the previous LACP PDU recv count for this interface, from our global dictionary.
        previous_pdus_rcvd = previous_intf_pdus_rcvd_dict[port]

        # If it increased too much compared to the last time we checked, raise a syslog and shutdown
        # the interface.
        if (pdus_rcvd > previous_pdus_rcvd + storm_limit):
            print("increase: %s, current=%d, previous=%d" % (port, pdus_rcvd, previous_pdus_rcvd))
            syslog_str = "[%s] LACP PDU storm on %s after %d second(s): count current=%d, previous=%d.  Shutting down interface" % \
                        (sdk.getAppName(), port, check_interval, pdus_rcvd, previous_pdus_rcvd)
            t.syslog(t.WARNING, str(syslog_str))
            shutdown_interface(port)

        # Keep a track of the PDU recv count for next time.
        previous_intf_pdus_rcvd_dict[port] = pdus_rcvd

def check_lacp_storm():
    global cliP, sdk, storm_limit

    t = sdk.getTracer()
    print("check_lacp_storm()")
    resp_str = cliP.execShowCmd("show lacp counters", nx_sdk_py.R_JSON)
    if (resp_str == ""):
        return
    resp_json = json.loads(resp_str)

    # If no counters at all, return.
    if ("TABLE_interface" not in resp_json):
        return

    row_interface = resp_json["TABLE_interface"]["ROW_interface"]

    # If just one port-channel, make it a list.  If not, it's already a list of port-channels.
    # Ideally NX-OS would always return a list in the CLI JSON output.
    if (type(row_interface) is not list):
        pc_list = [row_interface]
    else:
        pc_list = row_interface

    for current_entry in pc_list:
        check_port_channel(current_entry)

def timerThread(name, val):
    global cliP, sdk, check_interval

    while True:
        if sdk and cliP:
           print("timer kicked - sdk")
           check_lacp_storm()
        else:
           print("timer ticked - not sdk")
        time.sleep(check_interval)

class pyCmdHandler(nx_sdk_py.NxCmdHandler):
    def postCliCb(self, clicmd):
        global cliP, check_interval

        print("postCliCb")
        if ("set_check_interval_cmd" in clicmd.getCmdName()):
            if ("no" in clicmd.getCmdLineStr()):
                print("no set_check_interval_cmd")
                check_interval = 5
            else:
                print("set_check_interval_cmd")
                # Create Int Pointer to get the integer Value
                int_p = nx_sdk_py.new_intp()
                int_p = nx_sdk_py.void_to_int(clicmd.getParamValue("<check-interval-value>"))
                # Get the value of int * in python
                if int_p:
                    check_interval = int(nx_sdk_py.intp_value(int_p))
                print(check_interval)

        return True

def setup_clis():
    global cliP, sdk, mycmd

    cliP = sdk.getCliParser()

    nxcmd = cliP.newConfigCmd("set_check_interval_cmd", "check-interval <check-interval-value>")
    nxcmd.updateKeyword("check-interval", "Interval in seconds to check for LACP PDU storm")
    nxcmd.updateParam("<check-interval-value>", "Interval in seconds", nx_sdk_py.P_INTEGER)

    # Define our application callback for this new command
    mycmd = pyCmdHandler()
    cliP.setCmdHandler(mycmd)

    # Install the new commands to the NXOS parse tree
    cliP.addToParseTree()

# Perform the event handling loop in a dedicated Python thread.
# All SDK related activities happen here, while the main thread
# may continue to do other work.  The call to startEventLoop will
# block until we break out of it by calling stopEventLoop on
def evtThread(name,val):
    global sdk, event_hdlr

    sdk = nx_sdk_py.NxSdk.getSdkInst(len(sys.argv), sys.argv)
    if not sdk:
        return

    sdk.setAppDesc('LACP Storm Protect')

    t = sdk.getTracer()
    t.event("[%s] Started service" % sdk.getAppName())

    setup_clis()

    # Block in the event loop to service NXOS messages
    print("Starting event loop, CTRL-C to interrupt")
    sdk.startEventLoop()

    # Got here by calling stopEventLoop from signal handler
    t.event("Service quitting...!")
    event_hdlr = False

    # [Required] Needed for graceful exit.
    nx_sdk_py.NxSdk.__swig_destroy__(sdk)

# Create a timer thread
timer_thread = threading.Thread(target=timerThread, args=("timerThread",0))
timer_thread.daemon = True

# Create an event thread to register with NxSDK, CLI Parser, Tracer
# and Start Event loop to keep the application running.
# NOTE: Doesnt need a special Event Thread can be done on Main too.
evt_thread = threading.Thread(target=evtThread, args=("evtThread",0))

evt_thread.start()
timer_thread.start()
evt_thread.join()
