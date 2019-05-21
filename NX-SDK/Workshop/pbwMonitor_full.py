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
import random
# To gain access to Cisco NX-OS Infra SDK
import nx_sdk_py

# Global variables
cliP                            = 0
sdk                             = 0
event_hdlr                      = True
previous_intf_pdus_rcvd_dict    = {}
# in seconds
check_interval                  = 15
# in packets
storm_limit                     = 3
mycmd                           = 0
port_threshold = 100

### 
# Function to get the "show int" output and compute the percentage
# TX & RX Bandwidth utilization data.
###
def print_port_bw (result):
    global sdk, port_threshold

    t = sdk.getTracer()

    (interface, eth_bw, tx_rate, rx_rate, tx_bits, rx_bits) = ("", 0, 0, 0, 0, 0)

    ### Get all the necessary data to compute port BW utilization percentage
    for key in result:
        key_ascii = str(key.encode('ascii','ignore'))
        value_ascii = str(result[key].encode('ascii','ignore'))
        if "interface" in key_ascii:
           interface = value_ascii
        if "eth_bw" in key_ascii:
           eth_bw = int(value_ascii)
        if "eth_load_interval1_tx" in key_ascii:
           tx_rate = int(value_ascii)
        if "eth_load_interval1_rx" in key_ascii:
           rx_rate = int(value_ascii)
        if "eth_outrate1_bits" in key_ascii:
           tx_bits = int(value_ascii)
        if "eth_inrate1_bits" in key_ascii:
           rx_bits = int(value_ascii)

    bw_str = "%d Gbps (%d/%d)" % (eth_bw/1000000, rx_rate, tx_rate)

    ### Compute the TX & RX port BW utilization.
    tx_percentage = float(-1) # N/A
    rx_percentage = float(-1) # N/A

    if eth_bw: 
       # For test purposes
       tx_bits = random.randint(eth_bw, eth_bw * 1000) 

       tx_percentage = float((tx_bits * 100)/(eth_bw * 1000)) 
       rx_percentage = float((rx_bits * 100)/(eth_bw * 1000))     
     
    print_str = '{0:15} {1:20} {2:18.2f} {3:18.2f}'.format(interface, bw_str, tx_percentage, rx_percentage)      
    return print_str

class pyCmdHandler(nx_sdk_py.NxCmdHandler):
    def postCliCb(self, clicmd):
        global cliP, check_interval, port_threshold

        if "show_port_bw_util_cmd" in clicmd.getCmdName():
           
             ### Get the port value if set
             port = nx_sdk_py.void_to_string(clicmd.getParamValue("<port>"))
             if port:
                result = cliP.execShowCmd("show int %s" % str(port), \
                    nx_sdk_py.R_JSON)
             else:
                result = cliP.execShowCmd("show int", nx_sdk_py.R_JSON)

             ### Print header string for the show output
             print_str = 'Port BW Threshold limit: %d\n\n' % port_threshold
             print_str += '{0:15} {1:20} {2:18} {3:18}'.format("Interface", \
                "Bw (Rx/Tx Sec Rate)", "Tx_BW percentage", "RX_BW percentage")
             clicmd.printConsole("%s\n" % print_str)
             clicmd.printConsole("--------------- -------------------- " + \
                "------------------ ------------------\n") 

             ### Nothing to display
             if not result:
                return True

             ### Parse the JSON output
             json_res = json.loads(result)["TABLE_interface"]["ROW_interface"]
             for key in json_res:
                 
                 # Handle nested JSON output for all ports
                 if type(key) == dict:
                    display_op = print_port_bw(key)
                    if display_op:
                       clicmd.printConsole("%s\n" % display_op)
                 else:
                    # Handle JSON output for one port.
                    display_op = print_port_bw(json_res)
                    if display_op:
                       clicmd.printConsole("%s\n" % display_op)
                    break

        elif "port_bw_threshold_cmd" in clicmd.getCmdName():
             ### Action for port_bw_threshold_cmd

             ### Handle no command. Reset to default 
             if "no" in clicmd.getCmdLineStr():
                port_threshold = 100;
             else:
                ### Get the threshold value.
                int_p = nx_sdk_py.void_to_int(clicmd.getParamValue("<threshold>"))
                port_threshold = int(nx_sdk_py.intp_value(int_p))

        return True

def setup_show_cmd():
    global cliP, sdk, mycmd

    cliP = sdk.getCliParser()
    nxcmd = cliP.newShowCmd("show_port_bw_util_cmd", "port bw utilization [<port>]")
    nxcmd.updateKeyword("port", "Port Information")
    nxcmd.updateKeyword("bw", "Port Bandwidth Information")
    nxcmd.updateKeyword("utilization", "Port BW utilization in (%)")
    nxcmd.updateParam("<port>", "Optional Filter Port Ex) Ethernet1/1", \
        nx_sdk_py.P_INTERFACE)

def setup_config_cmd():
    global cliP, sdk, mycmd

    cliP = sdk.getCliParser()
    # Note: since we have already updated the keyword information for
    # "port" and "bw" earlier, we don't have to update for each and 
    # every cmd as its information will be automatically picked up for
    # other commands.
    nxcmd = cliP.newConfigCmd("port_bw_threshold_cmd", "port bw threshold <threshold>")
    nxcmd.updateKeyword("threshold", "Port BW Threshold in (%)")

    # Setting additional attributes for input parameter <threshold>
    # <threshold> should take a value only between 1-100.
    int_attr = nx_sdk_py.cli_param_type_integer_attr()
    int_attr.min_val = 1;
    int_attr.max_val = 100;
    nxcmd.updateParam("<threshold>", "Threshold Limit. Default 100%", nx_sdk_py.P_INTEGER, int_attr, len(int_attr))

def setup_clis():
    global cliP, sdk, mycmd

    cliP = sdk.getCliParser()

    # FIXME2: uncomment the following line
    setup_show_cmd()

    # FIXME3: uncomment the following line
    setup_config_cmd()

    # Add the command callback handler.
    mycmd = pyCmdHandler()
    cliP.setCmdHandler(mycmd)

    # Add custom commands to NX CLI Parse Tree
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

    sdk.setAppDesc('CLUS')

    # FIXME1: uncomment the following lines
    t = sdk.getTracer()
    t.event("[%s] Started app" % sdk.getAppName())

    setup_clis()

    # Block in the event loop to service NXOS messages
    print("Starting event loop, CTRL-C to interrupt")
    sdk.startEventLoop()

    # Got here by calling stopEventLoop from signal handler
    event_hdlr = False

    # [Required] Needed for graceful exit.
    nx_sdk_py.NxSdk.__swig_destroy__(sdk)

# Create an event thread to register with NxSDK, CLI Parser, Tracer
# and Start Event loop to keep the application running.
# NOTE: Doesnt need a special Event Thread can be done on Main too.
evt_thread = threading.Thread(target=evtThread, args=("evtThread",0))

evt_thread.start()
evt_thread.join()
