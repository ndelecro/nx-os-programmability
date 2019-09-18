#! /bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: setup.sh <ansible_base_dir>"
    return
fi
ansible_base_dir=$1

mv hosts $ansible_base_dir/
mv nxos_f5 nxos_f5_access nxos_f5_agg $ansible_base_dir/group_vars/
mv n9kv-1 n9kv-2 $ansible_base_dir/host_vars/
