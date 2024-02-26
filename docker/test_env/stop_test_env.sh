#!/bin/bash

docker_compose_file="rucio/etc/docker/dev/docker-compose.yml"

# stop the cluster
docker compose \
	--file $docker_compose_file \
	--file docker-compose-extension.yml \
	--profile storage \
	--profile extension \
	stop

# remove all containers
docker compose \
	--file $docker_compose_file \
	--file docker-compose-extension.yml \
	--profile storage \
	--profile extension \
	rm --force

sudo rm -rf /tmp/rucio_xrd1
