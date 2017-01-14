#! /usr/bin/python

import requests, json, sys
from N9K_NX_API import *

f = open('credentials', 'r')
switch_user = f.readline().rstrip()
switch_password = f.readline().rstrip()
vteps_file = sys.argv[1]
vlan_arg = sys.argv[2]
l2vni_arg = sys.argv[3]
mcast_group_arg = sys.argv[4]
access_port_arg = sys.argv[5]

def create_vlan_and_l2vni(switch, user, pwd, vlan, l2vni):
    my_clis = [
        "vlan %s" % (vlan), 
        "vn-segment %s" % (l2vni)
        ]
    post_clis(switch, user, pwd, my_clis)
    
def add_l2vni_to_nve_interface(switch, user, pwd, l2vni, mcast_group):
    my_clis = [
        "int nve1", 
        "member vni %s" % (l2vni),
        "mcast-group %s" % (mcast_group),
        "suppress-arp"
        ]
    post_clis(switch, user, pwd, my_clis)

def add_l2vni_to_evpn(switch, user, pwd, l2vni):
    my_clis = [
        "evpn",
        "vni %s l2" % (l2vni),
        "rd auto",
        "route-target import auto",
        "route-target export auto"
        ]
    post_clis(switch, user, pwd, my_clis)

def set_vlan_on_access_port(switch, user, pwd, vlan, access_port):
    my_clis = [
        "int %s" % (access_port),
        "switchport access vlan %s" % (vlan)
        ]
    post_clis(switch, user, pwd, my_clis)

def main():
    vteps = [line.rstrip('\n') for line in open(vteps_file)]
    for vtep in vteps:
        print("****** VTEP %s ******" % (vtep))
        create_vlan_and_l2vni(vtep, switch_user, switch_password,
                              vlan_arg, l2vni_arg)
        add_l2vni_to_nve_interface(vtep, switch_user, switch_password,
                                   l2vni_arg, mcast_group_arg)
        add_l2vni_to_evpn(vtep, switch_user, switch_password,
                          l2vni_arg)
        set_vlan_on_access_port(vtep, switch_user, switch_password,
                                vlan_arg, access_port_arg)
    
if __name__ == "__main__":
    main()
