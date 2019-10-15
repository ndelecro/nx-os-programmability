#! /bin/bash

hosts=(
    "ip1 host1"
    "ip2 host2"
)

for host in "${hosts[@]}"; do
    echo $host >> /etc/hosts
done
