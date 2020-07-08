#!/bin/bash
set -e
python /rucio-jupyterlab/docker/configure.py
exec "$@"