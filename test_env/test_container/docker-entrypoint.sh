#!/bin/bash

# Step zero, get a compliant proxy. The key must NOT be group/other readable
KEY=$(mktemp)
cat /opt/rucio/etc/userkey.pem > "$KEY"
#conda activate rucio_jupyterlab
/opt/conda/envs/rucio_jupyterlab/bin/xrdgsiproxy init -valid 9999:00 -cert /opt/rucio/etc/usercert.pem -key "$KEY"
rm -f "$KEY"

exec "$@"
