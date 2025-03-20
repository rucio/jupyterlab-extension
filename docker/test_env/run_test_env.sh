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

# Get the tag of the rucio-dev image corresponding to the rucio repository version
# Path to your Rucio repository
SCRIPT_DIR=$(dirname "$0")
REPO_PATH=$(realpath "$SCRIPT_DIR/rucio")

# Change directory to the Git repository
if cd "$REPO_PATH"; then
    # Get the Git tag
    RUCIO_TAG=$(git describe --tags --abbrev=0 2>/dev/null)

    if [ -n "$RUCIO_TAG" ]; then
        export RUCIO_IMG="release-$RUCIO_TAG"
    else
        export RUCIO_IMG="latest-alma9"
    fi

    # Change back to the original directory (optional)
    cd - >/dev/null 2>&1
else
  echo "Error: Could not access Git repository at $REPO_PATH."
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
	docker exec -it dev_rucio_1 /bin/bash -c "tools/run_tests.sh -ir"
fi
