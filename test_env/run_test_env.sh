#!/bin/bash

docker_compose_file="rucio/etc/docker/dev/docker-compose.yml"

# Run Docker Compose with the chosen file and profile
docker compose --file "$docker_compose_file" --profile storage up -d


# Login into rucio dev container and run some tests, create some RSEs, file uploads, file replication using rules 
# to have a working set-up of RUCIO server
docker exec -it dev-rucio-1 /bin/bash -c "tools/run_tests.sh -ir"

# Run the jupyterlab container
./run_jupyterlab_container.sh
