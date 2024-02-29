#!/bin/bash

# Create a shared folder to be used for the XRD1 RSE
# and the rucio-jupyterlab container
if [ ! -d /tmp/rucio_xrd1 ]
then
	mkdir -p /tmp/rucio_xrd1
	chmod 777 /tmp/rucio_xrd1
	RUN_TEST=1
else
	RUN_TEST=0
fi

# Run Docker Compose with the chosen file and profile
docker compose \
	--file rucio/etc/docker/dev/docker-compose.yml \
	--file docker-compose-extension.yml \
	--profile storage --profile extension up -d


# Login into rucio dev container and run some tests, create some RSEs,
# file uploads, file replication using rules 
# to have a working set-up of RUCIO server
# WARNING: if the test cluster wasn't properly closed this step will crash
if [ "$RUN_TEST" -eq "1" ]
then
	docker exec -it dev-rucio-1 /bin/bash -c "tools/run_tests.sh -ir"
fi
