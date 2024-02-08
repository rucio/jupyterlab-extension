#!/bin/bash

# Run Docker Compose with the chosen file and profile
docker compose \
	--file rucio/etc/docker/dev/docker-compose.yml \
	--file docker-compose-extension.yml \
	--profile storage up -d


# Login into rucio dev container and run some tests, create some RSEs,
# file uploads, file replication using rules 
# to have a working set-up of RUCIO server
# WARNING: if the test cluster wasn't properly closed this step will crash
docker exec -it dev-rucio-1 /bin/bash -c "tools/run_tests.sh -ir"
