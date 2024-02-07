#FROM docker.io/rucio/rucio-dev:latest-alma9
#FROM docker.io/rucio/rucio-dev:release-32.8.0
FROM jupyter/docker-stacks-foundation

# create the conda environment
ADD environment.yml /
RUN mamba env create -f /environment.yml

# add jupyter notebook configuration
ADD jupyter_server_config.py $HOME/.jupyter/jupyter_server_config.py
ADD jupyter_notebook_config.json $HOME/.jupyter/jupyter_notebook_config.json
ADD ipython_kernel_config.py $HOME/.ipython/profile_default/ipython_kernel_config.py
ADD rucio.cfg /opt/rucio/etc/rucio.cfg

USER root
RUN fix-permissions /home/jovyan
USER $NB_UID

# add script to install rucio-jupyterlab extension and its dependencies
ADD install_extension_and_run.sh /install_extension_and_run.sh

EXPOSE 8888

# Startup
ADD docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/install_extension_and_run.sh"]
