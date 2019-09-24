#! /bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: setup.sh <ansible_base_dir>"
    return
fi
ansible_base_dir=$1

mv hosts $ansible_base_dir/
mv nxos_vteps $ansible_base_dir/group_vars/
mv 92300-L1a-S2 93180EX-L3-S1 $ansible_base_dir/host_vars/
