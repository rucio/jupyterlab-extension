#!/bin/bash

# Get the tag of the rucio-dev image corresponding to the rucio repository version
# Path to your Rucio repository
SCRIPT_DIR=$(dirname "$0")
REPO_PATH=$(realpath "$SCRIPT_DIR/rucio")

# Change directory to the Git repository
if cd "$REPO_PATH"; then
    # Get the Git tag
    export RUCIO_TAG=$(git describe --tags --abbrev=0 2>/dev/null)

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
