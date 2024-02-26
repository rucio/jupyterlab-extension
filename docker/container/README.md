# build the docker image

## previous base jupyter-docker-stacks image


	git clone git@github.com:jupyter/docker-stacks.git jupyter-docker-stacks
	cd jupyter-docker-stacks/images/docker-stacks-foundation/

Tune the Dockerfile as you wish

In our case we set the python version to 3.9. Then we build the image to use it as the 
basis for our docker image.

	docker build . -t jupyter/docker-stacks-foundation:python-3.9

