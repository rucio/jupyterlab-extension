FROM jupyter/scipy-notebook
LABEL maintainer="Muhammad Aditya Hilmy <mhilmy@hey.com>"

USER root

COPY . /rucio-jupyterlab
RUN fix-permissions /rucio-jupyterlab
WORKDIR /rucio-jupyterlab

USER $NB_UID

RUN pip install .
RUN jupyter serverextension enable --py rucio_jupyterlab --sys-prefix
RUN jlpm
RUN jlpm build
RUN jupyter labextension link .

ENV JUPYTER_ENABLE_LAB=yes

WORKDIR $HOME
CMD ["/rucio-jupyterlab/docker/configure.sh", "start-notebook.sh"]