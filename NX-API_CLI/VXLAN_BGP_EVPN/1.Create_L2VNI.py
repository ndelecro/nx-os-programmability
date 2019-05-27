#! /usr/bin/python

import requests, json, sys
from nxapi import *

switch_user = "admin"
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

def check_vlan(switch, user, vlan):
    resp = post_clis(switch, user, ["show vlan id %s" % vlan])
    if resp["result"]["body"]["TABLE_vlanbriefid"]["ROW_vlanbriefid"] \
       ["vlanshowbr-vlanstate"] != "active":
        print("ERROR: VLAN %s validation failed on switch %s" % \
              (vlan, switch))

def main():
    get_switch_password()

    create_vlan_and_l2vni(vlan_arg, l2vni_arg)
    add_l2vni_to_nve(l2vni_arg, mcast_group_arg)
    add_l2vni_to_evpn(l2vni_arg)
    set_vlan_on_access_port(vlan_arg, access_port_arg)

    vteps = [line.rstrip('\n') for line in open(vteps_file)]
    for vtep in vteps:
        print("****** VTEP %s ******" % (vtep))
        post_clis(vtep, switch_user, clis)
        check_vlan(vtep, switch_user, vlan_arg)

if __name__ == "__main__":
    main()

