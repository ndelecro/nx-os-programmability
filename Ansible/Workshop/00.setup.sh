#! /bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 student_id"
    exit 1
fi

id=$1

for file in *.{yml,txt,j2}; do
    sed -i "s/STUDENT_ID/$id/" $file
    echo $file
done

sed -i "s/STUDENT_ID/$id/" /etc/ansible/host_vars/n9kv-{1,2}
