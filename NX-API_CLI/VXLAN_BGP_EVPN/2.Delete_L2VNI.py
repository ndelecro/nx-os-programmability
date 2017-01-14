#! /usr/bin/python

import requests, json, sys
from N9K_NX_API import *

f = open('credentials', 'r')
switch_user = f.readline().rstrip()
switch_password = f.readline().rstrip()
vteps_file = sys.argv[1]
vlan_arg = sys.argv[2]
l2vni_arg = sys.argv[3]
access_port_arg = sys.argv[4]

def delete_vlan_and_l2vni(switch, user, pwd, vlan):
    my_clis = [
        "no vlan %s" % (vlan)
        ]
    post_clis(switch, user, pwd, my_clis)
    
def remove_l2vni_from_nve_interface(switch, user, pwd, l2vni):
    my_clis = [
        "int nve1", 
        "no member vni %s" % (l2vni)
        ]
    post_clis(switch, user, pwd, my_clis)

def remove_l2vni_from_evpn(switch, user, pwd, l2vni):
    my_clis = [
        "evpn",
        "no vni %s l2" % (l2vni)
        ]
    post_clis(switch, user, pwd, my_clis)

def reset_vlan_on_access_port(switch, user, pwd, access_port):
    my_clis = [
        "int %s" % (access_port),
        "switchport access vlan 1"
        ]
    post_clis(switch, user, pwd, my_clis)

def main():
    vteps = [line.rstrip('\n') for line in open(vteps_file)]
    for vtep in vteps:
        print("****** VTEP %s ******" % (vtep))
        reset_vlan_on_access_port(vtep, switch_user, switch_password,
                                  access_port_arg)
        remove_l2vni_from_evpn(vtep, switch_user, switch_password,
                               l2vni_arg)
        remove_l2vni_from_nve_interface(vtep, switch_user, switch_password,
                                        l2vni_arg)
        delete_vlan_and_l2vni(vtep, switch_user, switch_password, 
                              vlan_arg)
    
if __name__ == "__main__":
    main()
