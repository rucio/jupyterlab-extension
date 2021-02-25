# Rucio JupyterLab Extension

![Github Actions Status](https://github.com/rucio/jupyterlab-extension/workflows/Build/badge.svg)

This is a JupyterLab extension that integrates with [Rucio - Scientific Data Management](https://github.com/rucio/rucio) to allow users to access some of Rucio's capabilities directly from the JupyterLab interface.


This extension is composed of a Python package named `rucio_jupyterlab`
for the server extension and a NPM package named `rucio-jupyterlab`
for the frontend extension.


## Requirements

* JupyterLab >= 3.0

## Install

Note: You will need NodeJS to install the extension.

```bash
pip install rucio-jupyterlab
```

If you are going to run the extension in Download mode, you will also need to install libraries required by the RSE downloaders. For instance, `gfal2`, which is available in EPEL or conda-forge. 

Additionally, you need to have `grid-proxy-init` or `voms-proxy-init` executable. You can do so by installing `voms-clients-java`.

```bash
$ apt install voms-clients-java
$ conda install -c conda-forge python-gfal2
# OR
$ yum install epel-release
$ yum install gfal2-all gfal2-python voms-clients-java
```

Restart your JupyterLab instance afterwards to load the server extension.

## Configuration

See [CONFIGURATION.md](CONFIGURATION.md)

## Contributing

If you want to contribute or build the extension from source, see [CONTRIBUTING.md](CONTRIBUTING.md)

## Quick Setup using Docker

This repository comes with a Docker image of [jupyter/scipy-notebook](https://hub.docker.com/r/jupyter/scipy-notebook) installed with the extension.

To run the image, use the following command.


#### Replica Mode

```bash
$ docker run -d -p 8888:8888 \
    -e RUCIO_MODE=replica \
    -e RUCIO_WILDCARD_ENABLED=<true = 1, false = 0> \
    -e RUCIO_BASE_URL=<Rucio base URL> \
    -e RUCIO_AUTH_URL=<Rucio auth URL (if any)> \
    -e RUCIO_DESTINATION_RSE=<destination RSE> \
    -e RUCIO_DISPLAY_NAME=<instance display name> \
    -e RUCIO_NAME=<instance name> \
    -e RUCIO_SITE_NAME=ROAMING \
    -e RUCIO_VO=def \
    -e RUCIO_PATH_BEGINS_AT=<path begins at> \
    -e RUCIO_RSE_MOUNT_PATH=<mount path> \
    -v <host folder>:<container folder> \
    rucio/jupyterlab:latest
```

`<host folder>` is a folder in the host that is mounted to a Rucio Storage Element via FUSE.
`<container folder>` is a folder accessible from the notebook that is mounted to the host folder.


#### Download Mode

```bash
$ docker run -d -p 8888:8888 \
    -e RUCIO_MODE=download \
    -e RUCIO_WILDCARD_ENABLED=<true = 1, false = 0> \
    -e RUCIO_BASE_URL=<Rucio base URL> \
    -e RUCIO_AUTH_URL=<Rucio auth URL (if any)> \
    -e RUCIO_DISPLAY_NAME=<instance display name> \
    -e RUCIO_NAME=<instance name> \
    -e RUCIO_SITE_NAME=ROAMING \
    -e RUCIO_VO=def \
    -e RUCIO_VOMS_ENABLED=<true = 1, false = 0> \
    -e RUCIO_VOMS_VOMSES_PATH=<path to vomses file (optional)> \
    -e RUCIO_VOMS_CERTDIR_PATH=<path to certdir (optional)> \
    -e RUCIO_VOMS_VOMSDIR_PATH=<path to vomsdir (optional)> \
    -e RUCIO_CA_CERT=/certs/rucio_ca.pem \
    -v <path to Rucio CA PEM file>:/certs/rucio_ca.pem \
    rucio/jupyterlab:latest
```

Follow the [configuration guide](CONFIGURATION.md) for details of the parameters.


## Troubleshoot

If you are seeing the frontend extension but it is not working, check
that the server extension is enabled:

```bash
jupyter serverextension list
```

If the server extension is installed and enabled but you are not seeing
the frontend, check the frontend is installed:

```bash
jupyter labextension list
```

If it is installed, try:

```bash
jupyter lab clean
jupyter lab build
```