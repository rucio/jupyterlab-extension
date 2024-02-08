# Rucio jupyterlab extension test environment

## Overview

This folder contains the necessary files and instructions to launch
a local Rucio cluster with the goal of testing the jupyterlab extension 
coupled to specific versions of Rucio and jupyterlab.

The cluster is an extension of the
[Rucio development cluster](https://github.com/rucio/rucio/tree/master/etc/docker/dev)
with an additional container (`rucio-jupyterlab`) containing a jupyterlab server 
with the checked-out version of the Rucio jupyterlab extension.

## Preparation

### Build the rucio-jupyterlab docker image

Modify the files in the `test_container` as desired.
Pay special attention to:
* `environment.yml`: environment definition (e.g. python version)
* `jupyter_notebook_config.yml`: Rucio jupyterlab extension configuration 

```
cd test_container
docker build . -t rucio-jupyterlab
```

### Choose the version of Rucio

Rucio is added as a git submodule.

If it's the first time you clone this repo,
you will have to run `git submodule init` to initialize it, and `git submodule update` to fetch
the updates.

Then you can choose the version of Rucio you want to use by doing a `git checkout`, for example:
```
cd rucio
git checkout 32.8.0
```

## Start/stop the development cluster

### Start the cluster

Execute the `run_test_env.sh` script to launch a development cluster.

This script will also create a temporary folder in `$TMP` (`/tmp/rucio_xrd1`) that will be shared between
the XRD1 RSE and the jupyterlab container to test the extension in replica mode.

The script also runs the tests to create some dummy data. If the temporary folder already exists,
it is assumed that the dummy data was already created and this step is skipped.

Once the script is executed it will take some time for the rucio-jupyterlab container
to be ready. It has to install all the dependencies, build the extension, ...
The progress of the setup can be tracked through the container logs
`docker logs -t dev-rucio-jupyterlab-1` . When the process finishes there will be 
this message in the logs
```
[I 2024-02-08 12:42:04.428 ServerApp] Jupyter Server 1.24.0 is running at:
[I 2024-02-08 12:42:04.428 ServerApp] http://693c5ea2930d:8888/lab
[I 2024-02-08 12:42:04.428 ServerApp]  or http://127.0.0.1:8888/lab
[I 2024-02-08 12:42:04.428 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
```
and the jupyterlab server will be accessible at http://localhost:8888


### Stop the cluster

Execute the `stop_test_env.sh` script to stop de cluster,
remove the containers and the temporary directory.

