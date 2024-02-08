#!/bin/bash

docker_compose_file="rucio/etc/docker/dev/docker-compose.yml"

# stop the cluster
docker compose -f $docker_compose_file --file docker-compose-extension.yml --profile storage stop

# remove all containers
docker compose -f $docker_compose_file --file docker-compose-extension.yml --profile storage rm --force

rm -rf /tmp/rucio_xrd1