#! /usr/bin/python

import requests, json, sys
from nxapi import *

switch_user = "admin"
vteps_file = "vteps"
vlan_arg = sys.argv[1]
l2vni_arg = sys.argv[2]
access_port_arg = sys.argv[3]

clis = []

def delete_vlan_and_l2vni(vlan):
    clis.append("no vlan %s" % vlan)

def remove_l2vni_from_nve(l2vni):
    clis.append("int nve1")
    clis.append("  no member vni %s" % l2vni)

def remove_l2vni_from_evpn(l2vni):
    clis.append("evpn")
    clis.append("  no vni %s l2" % l2vni)

def reset_access_port(access_port):
    clis.append("int %s" % access_port)
    clis.append("  switchport access vlan 1")

def main():
    get_switch_password()

    reset_access_port(access_port_arg)
    remove_l2vni_from_evpn(l2vni_arg)
    remove_l2vni_from_nve(l2vni_arg)
    delete_vlan_and_l2vni(vlan_arg)

    vteps = [line.rstrip('\n') for line in open(vteps_file)]
    for vtep in vteps:
        print("****** VTEP %s ******" % (vtep))
        post_clis(vtep, switch_user, clis)

if __name__ == "__main__":
    main()

