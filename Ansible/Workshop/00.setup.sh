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

for file in *.{yml,txt,j2}; do
    sed -i "s/STUDENT_ID/$id/" $file
    echo $file
done

sed -i "s/STUDENT_ID/$id/" /etc/ansible/group_vars/nxos_vteps

echo 172.16.255.50 n9kv-1 >> /etc/hosts
echo 172.16.255.51 n9kv-2 >> /etc/hosts
