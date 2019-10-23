#! /bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 student_id"
    exit 1
fi

id=$1

re='^[0-9]+$'
if ! [[ $id =~ $re ]] ; then
    echo "Error: student_id must be a number" >&2
    exit 1
fi

for file in ~/Ansible/Workshop/*.{yml,txt,j2,xml}; do
    sed -i "s/STUDENT_ID/$id/" $file
    echo $file
done

sed -i "s/STUDENT_ID/$id/" /etc/ansible/group_vars/nxos_vteps

cp ~/Ansible/Workshop/Admin/netconf_config.py /usr/local/lib/python2.7/dist-packages/ansible/modules/network/netconf/
