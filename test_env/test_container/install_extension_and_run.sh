#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate rucio_jupyterlab
cd /rucio-jupyterlab
pip install -e .
jupyter labextension develop --overwrite .
jlpm run build
jupyter server extension enable rucio_jupyterlab.server
jupyter lab --allow-root --ip 0.0.0.0 --no-browser --port 8888 --debug