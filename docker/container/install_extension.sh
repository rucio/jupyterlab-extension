#!/bin/bash

# install the rucio-jupyterlab extension
# if the purpose is develop, build it
# otherwise just install it
#eval "$(micromamba shell hook --shell bash )"
#micromamba activate base
cd /rucio-jupyterlab

if [ "$CONTAINER_PURPOSE" == "develop" ]
then
	pip install -e .
	jupyter labextension develop --overwrite .
	jlpm run build
	jupyter server extension enable rucio_jupyterlab.server
else
	pip install .
	jupyter serverextension enable --py rucio_jupyterlab --sys-prefix
	jupyter labextension link . --dev-build=False
	jupyter lab clean -y
	npm cache clean --force \
	    && rm -rf "/home/${NB_USER}/.cache/yarn" \
	    && rm -rf "/home/${NB_USER}/.node-gyp"
fi