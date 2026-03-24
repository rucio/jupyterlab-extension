FROM quay.io/jupyter/docker-stacks-foundation:python-3.12
LABEL maintainer="Muhammad Aditya Hilmy <mhilmy@hey.com>, Francesc Torradeflot <torradeflot@pic.es>, Giovanni Guerrieri <giovanni.guerrieri@cern.ch>"

ENV CONTAINER_PURPOSE="test"
ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="100"

USER $NB_UID

# Install additional dependencies via mamba, and ensure all packages are up to date.
RUN mamba update --all -y -n base -c conda-forge \
    && mamba install -y -n base -c conda-forge \
                python-gfal2 \
                "nodejs>=20.0.0" \
                pip \
    && mamba clean --all -f -y

USER root

# Final clean up to reduce image size
RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

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