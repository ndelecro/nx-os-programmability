#! /bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 {container-name}"
    exit 1
fi

container=$1
docker cp hosts.sh $container:/tmp
docker exec $container /tmp/hosts.sh
