#!/bin/bash

docker_compose_file="rucio/etc/docker/dev/docker-compose.yml"

docker compose -f $docker_compose_file --profile storage stop
docker compose -f $docker_compose_file --profile storage rm --force

docker stop rucio-jupyterlab
