#! /usr/bin/python

import requests, json, sys
from N9K_NX_API import *

f = open('credentials', 'r')
switch_user = f.readline().rstrip()
switch_password = f.readline().rstrip()
vteps_file = "vteps"
vlan_arg = sys.argv[1]
l2vni_arg = sys.argv[2]
mcast_group_arg = sys.argv[3]
access_port_arg = sys.argv[4]

clis = []

def create_vlan_and_l2vni(vlan, l2vni):
    clis.append("vlan %s" % vlan)
    clis.append("  vn-segment %s" % l2vni)

def add_l2vni_to_nve(l2vni, mcast_group):
    clis.append("int nve1")
    clis.append("  member vni %s" % l2vni)
    clis.append("  mcast-group %s" % mcast_group)
    clis.append("  suppress-arp")

def add_l2vni_to_evpn(l2vni):
    clis.append("evpn")
    clis.append("  vni %s l2" % l2vni)
    clis.append("  rd auto")
    clis.append("  route-target import auto")
    clis.append("  route-target export auto")

def set_vlan_on_access_port(vlan, access_port):
    clis.append("int %s" % access_port)
    clis.append("  switchport access vlan %s" % vlan)

def main():
    create_vlan_and_l2vni(vlan_arg, l2vni_arg)
    add_l2vni_to_nve(l2vni_arg, mcast_group_arg)
    add_l2vni_to_evpn(l2vni_arg)
    set_vlan_on_access_port(vlan_arg, access_port_arg)

    print(clis)

    vteps = [line.rstrip('\n') for line in open(vteps_file)]
    for vtep in vteps:
        print("****** VTEP %s ******" % (vtep))
        post_clis(vtep, switch_user, switch_password, clis)

if __name__ == "__main__":
    main()

