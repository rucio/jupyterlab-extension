# Rucio jupyterlab extension docker image

## Building the image

### Base image: jupyter/docker-stacks-foundation

We rely on the `docker-stacks-foundation` image from the
[Jupyter Docker Stacks repository](https://github.com/jupyter/docker-stacks/tree/main).

It is an image containing a minimal conda/mamba environment, we want to use this image to make
sure the extension works in a "clean" environment.

You can pull this image from 

	docker pull quay.io/jupyter/docker-stacks-foundation:python-3.11

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
