#! /bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 {create|delete|test}"
    exit 1
fi

action=$1

for id in {10..42}; do
    container=student$id
    echo $container
    if [ "$action" = "create" ]; then
	echo create
	docker run -d --name=$container --hostname=$container -it ndelecro/nx-os-programmability bash
	docker exec $container ~/Ansible/Workshop/Admin/setup_ansible.sh $id
	docker cp hosts.sh $container:/tmp
	docker exec $container /tmp/hosts.sh
    fi

    if [ "$action" = "delete" ]; then
	echo delete
	docker stop $container
	docker rm $container
    fi

    if [ "$action" = "test" ]; then
        docker exec student42 ping -c 1 n9kv-1
        docker exec student42 ping -c 1 n9kv-2
    fi
done
