#!/bin/bash

RUCIO_DIR=$(realpath "rucio")
echo RUCIO_DIR=$RUCIO_DIR
RUCIO_ETC=$RUCIO_DIR/etc
RUCIO_JUPYTERLAB_DIR=$(realpath "..")

FULL_PATH_TO_SCRIPT="$(realpath "${BASH_SOURCE[-1]}")"
SCRIPT_DIRECTORY="$(dirname "$FULL_PATH_TO_SCRIPT")"

docker run --rm \
      -v $RUCIO_ETC/certs/rucio_ca.pem:/etc/grid-security/certificates/5fca1cb1.0 \
      -v $RUCIO_ETC/certs/hostcert_rucio.pem:/etc/grid-security/hostcert.pem \
      -v $RUCIO_ETC/certs/hostcert_rucio.key.pem:/etc/grid-security/hostkey.pem \
      -v $RUCIO_ETC/certs/rucio_ca.pem:/opt/rucio/etc/rucio_ca.pem \
      -v $RUCIO_ETC/certs/ruciouser.pem:/opt/rucio/etc/usercert.pem \
      -v $RUCIO_ETC/certs/ruciouser.key.pem:/opt/rucio/etc/userkey.pem \
      -v $RUCIO_JUPYTERLAB_DIR:/rucio-jupyterlab \
      -e X509_USER_CERT=/opt/rucio/etc/usercert.pem \
      -e X509_USER_KEY=/opt/rucio/etc/userkey.pem \
      -e RUCIO_CA_CERT=/opt/rucio/etc/rucio_ca.pem \
      -p 8888:8888 \
      --network dev_default \
      --name rucio-jupyterlab \
      -ti \
      rucio-jupyterlab #\
#      /bin/bash
#      /root/miniforge3/envs/rucio_jupyterlab/bin/jupyter lab --allow-root --ip 0.0.0.0 --debug --no-browser --port 8888
#      -v $RUCIO_ETC/certs/ruciouser.certkey.pem:/opt/rucio/etc/usercertkey.pem \
#      -v $RUCIO_ETC/certs/ssh/ruciouser_sshkey.pub:/root/.ssh/ruciouser_sshkey.pub \
#      -v $RUCIO_ETC/certs/ssh/ruciouser_sshkey:/root/.ssh/ruciouser_sshkey \
#      -v $SCRIPT_DIRECTORY/jupyter_notebook_config.json:/home/jovyan/.jupyter/jupyter_notebook_config.json \
      
