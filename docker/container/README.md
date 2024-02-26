# Rucio jupyterlab extension docker image

## Building the image

### Base image: jupyter/docker-stacks-foundation

We rely on the `docker-stacks-foundation` image from the
[Jupyter Docker Stacks repository](https://github.com/jupyter/docker-stacks/tree/main).

It is an image containing a minimal conda/mamba environment, we want to use this image to make
sure the extension works in a "clean" environment.

### Building a custom base image

In our case we want to set the python version to 3.9, and there's no image publicly available with this version.

So we clone the [Jupyter Docker Stacks repository](https://github.com/jupyter/docker-stacks/tree/main)

	git clone git@github.com:jupyter/docker-stacks.git jupyter-docker-stacks
	cd jupyter-docker-stacks/images/docker-stacks-foundation/

Tune the Dockerfile to install python=3.9, and build/tag the image that will be used as the basis
for our `rucio-jupyterlab` image.

	docker build . -t jupyter/docker-stacks-foundation:python-3.9

### Building the `rucio-jupyterlab` docker image

From the root folder of the project, run

	docker build . -t rucio-jupyterlab -f docker/container/Dockerfile
	
## Using the image

### Standalone

Check the instructions in [the main README](../../README.md) to see how to use the image
standalone, that is without the rest of the Rucio development environment

### Inside Rucio's development environment

Check the instructions on [how to use the test environment](../test_env/README.md) to 
see how to use this image together with the Rucio development environment.
