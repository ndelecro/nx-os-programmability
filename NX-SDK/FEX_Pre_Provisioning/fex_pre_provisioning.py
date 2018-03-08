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
import os.path
# To gain access to Cisco NXOS Infra SDK
import nx_sdk_py

# Global Variables
cliP                = 0
sdk                 = 0
event_hdlr          = True
# In seconds
DELAY_BETWEEN_CHECK = 5
fex_id = 0

def configure_fex(fex_id):
    global sdk

    print("configure_fex(%d)" % fex_id)
    t = sdk.getTracer()

    # check if config file exists: fex-FEX_ID-config
    file_name = "fex-%d-config" % fex_id
    print file_name
    if (os.path.isfile(file_name) == False):
        err_str = "Cannot find config file %s" % file_name
        print(err_str)
        t.syslog(t.WARNING, err_str)
        return

    print("found FEX config file %s" % file_name)
    # VSH does not allow taking files from /bootflash, so copy to /tmp
    os.system("cp %s /tmp" % file_name)
    os.system("vsh -r /tmp/%s" % file_name)
    syslog_str = "Configured FEX %d with config file %s" % (fex_id, file_name)
    print(syslog_str)
    t.syslog(t.NOTICE, syslog_str)

def check_fex():
    global cliP, sdk, fex_id

    t = sdk.getTracer()
    print("check_fex()")

    show_cmd = "show fex"
    resp_json = json.loads(cliP.execShowCmd(show_cmd, nx_sdk_py.R_JSON))
    # if there's no entries, exit
    if ("TABLE_fex" not in resp_json):
        return

    fex_table_base = resp_json["TABLE_fex"]["ROW_fex"]
    # is this a new FEX?
    if (fex_table_base["fex_state"] == "Online"):
        new_fex_id = int(fex_table_base["fex_number"])
        if (new_fex_id != fex_id):
            syslog_str = "New FEX found Online: %d" % new_fex_id
            print(syslog_str)
            t.syslog(t.INFO, syslog_str)
            fex_id = new_fex_id
            configure_fex(new_fex_id)

def timerThread(name,val):
    global cliP, sdk

    while True:
        if sdk and cliP:
            print "timer kicked - sdk"
            check_fex()
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

    sdk.setAppDesc('FEX Pre Provisioning')

    t = sdk.getTracer()
    t.event("[%s] Started service" % sdk.getAppName())

    cliP = sdk.getCliParser()

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


