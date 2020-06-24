# Rucio JupyterLab Extension

![Github Actions Status](https://github.com/didithilmy/rucio-jupyterlab/workflows/Build/badge.svg)

This is a JupyterLab extension that integrates with [Rucio - Scientific Data Management](https://github.com/rucio/rucio) to allow users to access some of Rucio's capabilities directly from the JupyterLab interface.


This extension is composed of a Python package named `rucio_jupyterlab`
for the server extension and a NPM package named `rucio-jupyterlab`
for the frontend extension.


## Requirements

* JupyterLab >= 2.0

## Install

Note: You will need NodeJS to install the extension.

```bash
pip install rucio_jupyterlab
jupyter lab build
```

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