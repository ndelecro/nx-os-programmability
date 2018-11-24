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

# Global Variables
cliP                 = 0
sdk                  = 0
event_hdlr           = True
prev_load_list       = []
# in minutes
check_interval       = 10

def shutdown_interface(intf):
    file = open("/tmp/nxsdk_cmd", "w")
    file.write("int %s\n" % intf)
    file.write("shut\n")
    file.close()
    os.system("cat /tmp/nxsdk_cmd")
    cliP.execConfigCmd("/tmp/nxsdk_cmd")

def check_storm():
    global cliP, sdk, prev_load_list

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
                    syslog_str = "[%s] Traffic storm persisting on %s after %d minute(s): suppression discard count current=%d, previous=%d.  Shutting down interface" % \
                        (sdk.getAppName(), intf, check_interval, load, prev_load)
                    t.syslog(t.WARNING, str(syslog_str))
                    shutdown_interface(intf)

    prev_load_list = current_load_list

def timerThread(name,val):
    global cliP, sdk, check_interval

    while True:
        if sdk and cliP:
           print "timer kicked - sdk"
           check_storm()
        else:
           print "timer ticked - not sdk"
        time.sleep(check_interval)

# Perform the event handling loop in a dedicated Python thread.
# All SDK related activities happen here, while the main thread
# may continue to do other work.  The call to startEventLoop will
# block until we break out of it by calling stopEventLoop on
def evtThread(name,val):
    global cliP, sdk, event_hdlr

    sdk = nx_sdk_py.NxSdk.getSdkInst(len(sys.argv), sys.argv)
    if not sdk:
        return

    sdk.setAppDesc('Storm')

    t = sdk.getTracer()
    t.event("[%s] Started service" % sdk.getAppName())

    cliP = sdk.getCliParser()

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

# Create a Event Thread to register with NxSDK, CLI Parser, Tracer
# and Start Event loop to keep the application running.
# NOTE: Doesnt need a special Event Thread can be done on Main too.
evt_thread = threading.Thread(target=evtThread, args=("evtThread",0))

evt_thread.start()
timer_thread.start()
evt_thread.join()
