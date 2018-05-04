#! /isan/bin/python

import signal
import datetime
import time
import threading
import sys
import os
import json
# To gain access to Cisco NX-OS Infra SDK
import nx_sdk_py

# Global variables
cliP                = 0
sdk                 = 0
event_hdlr          = True
bw_threshold        = 100000000000
intf_list           = []
# In seconds
DELAY_BETWEEN_CHECK = 5
ribMgr              = 0

def debug_log(str):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    str_log = "%s -- %s" % (current_time, str)
    file = open("/tmp/ecmp_monitoring.log", "a")
    file.write(str_log + "\n")
    file.close()
    print(str_log)

def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           debug_log("obj.%s = %s" % (attr, getattr(obj, attr)))

def check_intf_load(intf):
    global cliP, sdk

    t = sdk.getTracer()
    show_cmd = "show interface %s" % (str(intf))
    resp_json = json.loads(cliP.execShowCmd(show_cmd, nx_sdk_py.R_JSON))
    # if there's no entries, exit
    if ("TABLE_interface" not in resp_json):
        return
    out_rate = resp_json["TABLE_interface"]["ROW_interface"]["eth_outrate1_bits"]
    if (int(out_rate) > bw_threshold):
        syslog_str = "[%s] High egress bandwidth: int=%s, bw=%s" % \
                      (sdk.getAppName(), intf, out_rate)
        t.syslog(t.WARNING, str(syslog_str))
        debug_log(syslog_str)

def get_telemetry_json():
    fields = ["interface", "eth_outrate1_bits"]

    debug_log("get_telemetry_json()")
    for intf in intf_list:
        show_cmd = "show interface %s" % (str(intf))
        debug_log(show_cmd)
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

        if (clicmd.isKeywordSet("tm-use-only")):
            debug_log("tm-use")
            tel_json = get_telemetry_json()
            debug_log(json.dumps(tel_json))
            clicmd.printConsole(json.dumps(tel_json))
            return True
        if ("set_bw_threshold_cmd" in clicmd.getCmdName()):
            if ("no" in clicmd.getCmdLineStr()):
                debug_log("no set_bw_threshold_cmd")
                bw_threshold = 10000000000
            else:
                debug_log("set_bw_threshold_cmd")
                # Create Int Pointer to get the integer Value
                int_p = nx_sdk_py.new_intp()
                int_p = nx_sdk_py.void_to_int(clicmd.getParamValue("<bw-threshold-value>"))
                # Get the value of int * in python
                if int_p:
                    bw_threshold = int(nx_sdk_py.intp_value(int_p)) * 1000000
                debug_log(bw_threshold)
        return True

### Overloaded NxRibMgrHandler class.
class pyRibHandler(nx_sdk_py.NxRibMgrHandler):
    def postL3RouteCb(self,nxroute):
        global intf_list, ribMgr, sdk

        debug_log("postL3RouteCb")
        prefix = nxroute.getAddress() + str("/") + str(nxroute.getMaskLen())
        debug_log(prefix)

        if (nxroute.getL3NextHopCount() > 1):
            debug_log("%s is a ECMP route" % prefix)
            # It's a ECMP route, let's get the outgoing interfaces
            nextHop = nxroute.getL3NextHop(True)
            while nextHop:
                debug_log("----> while nextHop")
                outAddr = nextHop.getAddress()
                outInterface = nextHop.getOutInterface()
                debug_log("----> %s, %s" % (outAddr, outInterface))
                # Let's get the actual p2p link outgoing interface
                p2pIntfRoute = ribMgr.getL3Route(outAddr)
                p2pIntfNextHop = p2pIntfRoute.getL3NextHop()
                p2pIntfName = p2pIntfNextHop.getOutInterface()
                debug_log("----> p2pIntfName: %s" % p2pIntfName)
                intf_list.append(p2pIntfName)
                nextHop = nxroute.getL3NextHop(False)
            syslog_str = "[%s] Found an ECMP bundle: %s --> %s" % \
              (sdk.getAppName(), prefix, ', '.join(map(str, intf_list)))
            t = sdk.getTracer()
            t.event(syslog_str)
        debug_log("end postL3RouteCb")
        return True

def timerThread(name,val):
    global cliP, sdk

    while True:
        if (sdk and cliP):
            for intf in intf_list:
                check_intf_load(intf)
        time.sleep(DELAY_BETWEEN_CHECK)

# Perform the event handling loop in a dedicated Python thread.
# All SDK related activities happen here, while the main thread
# may continue to do other work.  The call to startEventLoop will
# block until we break out of it by calling stopEventLoop on
def evtThread(name,val):
    global cliP, sdk, event_hdlr, ribMgr

    sdk = nx_sdk_py.NxSdk.getSdkInst(len(sys.argv), sys.argv)
    if (not sdk):
        return

    sdk.setAppDesc("ECMP Monitoring")

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
    cliP.addToParseTree()

    ribMgr = sdk.getRibMgr()
    myribcb = pyRibHandler()
    ribMgr.setRibMgrHandler(myribcb)
    ribMgr.watchL3Route("bgp", "65000")

    # Block in the event loop to service NX-OS messages
    debug_log("Starting event loop, CTRL-C to interrupt")
    sdk.startEventLoop()

    # Got here by calling stopEventLoop from signal handler
    t.event("Service Quitting...!")
    event_hdlr = False

    # Needed for graceful exit.
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
