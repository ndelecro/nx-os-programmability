#! /bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 {create|delete}"
    exit 1
fi

action=$1

for id in {10..30}; do
    container=student$id
    echo $container
    if [ "$action" = "create" ]; then
	echo create
	docker run -d --name=$container --hostname=$container -it ndelecro/nx-os-programmability bash
	docker exec $container ~/Ansible/Workshop/00.setup.sh $id
    fi

    if [ "$action" = "delete" ]; then
	echo delete
	docker stop $container
	docker rm $container
    fi
done

