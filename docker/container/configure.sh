#!/bin/bash
set -e
echo "Configuring Rucio jupyterlab extension"
python /rucio-jupyterlab/docker/container/configure.py
exec "$@"