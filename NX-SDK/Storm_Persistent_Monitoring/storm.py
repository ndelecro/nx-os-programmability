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
cliP                 = 0
sdk                  = 0
event_hdlr           = True
prev_load_list       = []
shut_dict            = {}
# in seconds
shut_interval        = 10
# in seconds
unshut_interval      = 60
mycmd                = 0

def shutdown_interface(intf):
    file = open("/tmp/nxsdk_cmd", "w")
    file.write("int %s\n" % intf)
    file.write("shut\n")
    file.close()
    os.system("cat /tmp/nxsdk_cmd")
    cliP.execConfigCmd("/tmp/nxsdk_cmd")

def unshut_interface(intf):
    file = open("/tmp/nxsdk_cmd", "w")
    file.write("int %s\n" % intf)
    file.write("no shut\n")
    file.close()
    os.system("cat /tmp/nxsdk_cmd")
    cliP.execConfigCmd("/tmp/nxsdk_cmd")

def unshut_interfaces():
    global sdk, shut_dict

    t = sdk.getTracer()
    for intf, timestamp in shut_dict.items():
        if (time.time() - timestamp > unshut_interval):
            print("unshutting interface %s" % intf)
            syslog_str = "[%s] Interface %s has been shut for more than %d seconds, unshutting" % \
                        (sdk.getAppName(), intf, unshut_interval)
            t.syslog(t.WARNING, str(syslog_str))
            unshut_interface(intf)
            # remove the entry from the list
            del shut_dict[intf]

def check_storm():
    global cliP, sdk, prev_load_list, shut_list

    t = sdk.getTracer()
    print("check_storm()")
    resp_str = cliP.execShowCmd("show interface counters storm-control", nx_sdk_py.R_JSON)
    resp_json = json.loads(resp_str)

    # First time we run, just copy the list and return
    current_load_list = resp_json["TABLE_interface"]["ROW_interface"]
    if (prev_load_list == []):
        prev_load_list = current_load_list
        return

    for current_entry in current_load_list:
        intf = current_entry["interface"]
        load = int(current_entry["eth_total_supp"])
        # Grab the previous storm load for this interface from the global table
        for prev_entry in prev_load_list:
            if (prev_entry["interface"] == intf):
                prev_load = int(prev_entry["eth_total_supp"])
                if (load > prev_load):
                    print("increase: %s, current=%d, previous=%d" % (intf, load, prev_load))
                    syslog_str = "[%s] Traffic storm persisting on %s after %d second(s): suppression discard count current=%d, previous=%d.  Shutting down interface" % \
                        (sdk.getAppName(), intf, shut_interval, load, prev_load)
                    t.syslog(t.WARNING, str(syslog_str))
                    shutdown_interface(intf)
                    # keep a track of the intf shut and the time
                    shut_dict[intf] = time.time()

    prev_load_list = current_load_list

def timerThread(name, val):
    global cliP, sdk, shut_interval

    while True:
        if sdk and cliP:
           print("timer kicked - sdk")
           check_storm()
           unshut_interfaces()
        else:
           print("timer ticked - not sdk")
        time.sleep(shut_interval)

class pyCmdHandler(nx_sdk_py.NxCmdHandler):
    def postCliCb(self, clicmd):
        global cliP, shut_interval, unshut_interval

        print("postCliCb")
        if ("set_shut_interval_cmd" in clicmd.getCmdName()):
            if ("no" in clicmd.getCmdLineStr()):
                print("no set_shut_interval_cmd")
                shut_interval = 60
            else:
                print("set_shut_interval_cmd")
                # Create Int Pointer to get the integer Value
                int_p = nx_sdk_py.new_intp()
                int_p = nx_sdk_py.void_to_int(clicmd.getParamValue("<shut-interval-value>"))
                # Get the value of int * in python
                if int_p:
                    shut_interval = int(nx_sdk_py.intp_value(int_p))
                print(shut_interval)

        if ("set_unshut_interval_cmd" in clicmd.getCmdName()):
            if ("no" in clicmd.getCmdLineStr()):
                print("no set_unshut_interval_cmd")
                unshut_interval = 60
            else:
                print("set_unshut_interval_cmd")
                # Create Int Pointer to get the integer Value
                int_p = nx_sdk_py.new_intp()
                int_p = nx_sdk_py.void_to_int(clicmd.getParamValue("<unshut-interval-value>"))
                # Get the value of int * in python
                if int_p:
                    unshut_interval = int(nx_sdk_py.intp_value(int_p))
                print(unshut_interval)
        return True

def setup_clis():
    global cliP, sdk, mycmd

    cliP = sdk.getCliParser()

    nxcmd = cliP.newConfigCmd("set_shut_interval_cmd", "shut-interval <shut-interval-value>")
    nxcmd.updateKeyword("shut-interval", "Interval in seconds after which the interfaces on which storm traffic persists are shut down")
    nxcmd.updateParam("<shut-interval-value>", "Interval in seconds", nx_sdk_py.P_INTEGER)

    nxcmd = cliP.newConfigCmd("set_unshut_interval_cmd", "unshut-interval <unshut-interval-value>")
    nxcmd.updateKeyword("unshut-interval", "Interval in seconds after which the interfaces that got shut down by the app are brought back up")
    nxcmd.updateParam("<unshut-interval-value>", "Interval in seconds", nx_sdk_py.P_INTEGER)

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

    sdk.setAppDesc('Storm')

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
