#!/bin/bash

# install the rucio-jupyterlab extension
# if the purpose is develop, build it
# otherwise just install it
cd /rucio-jupyterlab

if [ "$CONTAINER_PURPOSE" == "develop" ]
then
	pip install -e .
	jupyter labextension develop --overwrite .
	jlpm run build
	jupyter server extension enable rucio_jupyterlab.server
else
	# install from source
	pip install .
	# clean cache and node modules to reduce the image size
	jupyter lab clean -y
	npm cache clean --force \
	    && rm -rf "/home/${NB_USER}/.cache/yarn" \
	    && rm -rf "/home/${NB_USER}/.node-gyp" \
		&& rm -rf /rucio-jupyterlab/node_modules
fi