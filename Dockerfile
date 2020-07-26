FROM jupyter/scipy-notebook
LABEL maintainer="Muhammad Aditya Hilmy <mhilmy@hey.com>"

USER root
COPY . /rucio-jupyterlab

RUN conda install -y -c conda-forge python-gfal2 \
    && conda clean --all -f -y \
    && fix-permissions /rucio-jupyterlab \
    && sed -i -e 's/\r$/\n/' /rucio-jupyterlab/docker/configure.sh

WORKDIR /rucio-jupyterlab

USER $NB_UID

RUN pip install -e . \
    && jupyter serverextension enable --py rucio_jupyterlab --sys-prefix \
    && jlpm \
    && jlpm build \
    && jupyter labextension link . --dev-build=False \
    && jupyter lab clean -y \
    && npm cache clean --force \
    && rm -rf "/home/${NB_USER}/.cache/yarn" \
    && rm -rf "/home/${NB_USER}/.node-gyp"

ENV JUPYTER_ENABLE_LAB=yes

WORKDIR $HOME
CMD ["/rucio-jupyterlab/docker/configure.sh", "start-notebook.sh"]