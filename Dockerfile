FROM jupyter/scipy-notebook
LABEL maintainer="Muhammad Aditya Hilmy <mhilmy@hey.com>"

USER root

RUN conda install -y -c conda-forge python-gfal2 \
    && conda clean --all --yes 

COPY . /rucio-jupyterlab
RUN fix-permissions /rucio-jupyterlab \
    && sed -i -e 's/\r$/\n/' /rucio-jupyterlab/docker/configure.sh

WORKDIR /rucio-jupyterlab

USER $NB_UID

RUN pip install -e . \
    && jupyter serverextension enable --py rucio_jupyterlab --sys-prefix \
    && jlpm \
    && jlpm build \
    && jupyter labextension install .

ENV JUPYTER_ENABLE_LAB=yes

WORKDIR $HOME
CMD ["/rucio-jupyterlab/docker/configure.sh", "start-notebook.sh"]