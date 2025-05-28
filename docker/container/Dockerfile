FROM quay.io/jupyter/docker-stacks-foundation:python-3.11
LABEL maintainer="Muhammad Aditya Hilmy <mhilmy@hey.com>, Francesc Torradeflot <torradeflot@pic.es>"

ENV CONTAINER_PURPOSE="test"
ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="100"

USER $NB_UID

RUN mamba install -y -n base -c conda-forge \
		python-gfal2 \
		nodejs \
		pip \
    && mamba clean --all -f -y 

USER root

COPY . /rucio-jupyterlab
WORKDIR /rucio-jupyterlab

RUN fix-permissions /rucio-jupyterlab \
    && sed -i -e 's/\r$/\n/' /rucio-jupyterlab/docker/container/configure.sh

COPY docker/container/jupyter_server_config.json $HOME/.jupyter/jupyter_server_config.json
RUN fix-permissions $HOME/.jupyter
RUN mkdir -p /opt/rucio/etc \
	&& chown -R ${NB_UID}:${NB_GID} /opt/rucio/etc

USER $NB_UID

RUN /rucio-jupyterlab/docker/container/install_extension.sh

ENV JUPYTER_ENABLE_LAB=yes

WORKDIR $HOME
ENTRYPOINT ["/rucio-jupyterlab/docker/container/docker-entrypoint.sh"]
CMD ["/rucio-jupyterlab/docker/container/configure.sh", "/rucio-jupyterlab/docker/container/start_notebook.sh"]

USER ${NB_UID}