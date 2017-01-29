#! /usr/bin/python

import requests, json, sys, time
from N9K_NX_API import *

f = open('credentials', 'r')
switch_user = f.readline().rstrip()
switch_password = f.readline().rstrip()
switches_file = sys.argv[1]

# in nanoseconds
MAX_CORRECTION_VAL = 10
MAX_ENTRIES_TO_CHECK = 5
# in seconds
DELAY_BETWEEN_CHECK = 5

def check_ptp_corrections(switch, user, pwd):
    resp = post_clis(switch, user, pwd, ["show ptp corrections"])
    entry_count = 1
    for entry in resp["result"]["body"]["TABLE_ptp"]["ROW_ptp"]:
        correction_val = entry["correction-val"]
        if (int(correction_val) > MAX_CORRECTION_VAL):
            time = entry["sup-time"]
            print("PTP correction too high: switch=%s, correction=%s, time=%s" %
                  (switch, correction_val, time))
        if (entry_count > MAX_ENTRIES_TO_CHECK):
            return
        entry_count += 1

def main():
    switches = [line.rstrip('\n') for line in open(switches_file)]
    while (1):
        for switch in switches:
            print("***** Switch %s *****" % (switch))
            check_ptp_corrections(switch, switch_user, switch_password)
        time.sleep(DELAY_BETWEEN_CHECK)
    
if __name__ == "__main__":
    main()
