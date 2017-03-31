#! /usr/bin/python

import requests, json, sys, time
from N9K_NX_API import *
from time import gmtime, strftime

f = open('credentials', 'r')
switch_user = f.readline().rstrip()
switch_password = f.readline().rstrip()
switch = sys.argv[1]
interface = sys.argv[2]
max_load = sys.argv[3]

# in seconds
DELAY_BETWEEN_CHECK = 5

def check_intf_load(switch, interface, max_load, user, pwd):
    cli = "show interface " + interface
    resp = post_clis(switch, user, pwd, [cli])
    load = resp["result"]["body"]["TABLE_interface"]["ROW_interface"]["eth_inrate1_bits"]
    if (int(load) > int(max_load)):
        print("%s - Interface load too high: switch=%s, load=%s" %
              (strftime("%Y-%m-%d %H:%M:%S", gmtime()), switch, load))
    else:
        print("BBBB")
        
def main():
    while (1):
        check_intf_load(switch, interface, max_load, switch_user, switch_password)
        time.sleep(DELAY_BETWEEN_CHECK)
    
if __name__ == "__main__":
    main()
