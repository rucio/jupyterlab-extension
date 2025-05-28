# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from .handlers import setup_handlers
from .logging_config import setup_logging
import logging

def load_jupyter_server_extension(server_app):  # pragma: no cover
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app : jupyter_server.serverapp.ServerApp
        Jupyter Server application instance.
    """
    setup_handlers(server_app.web_app)
    server_app.log.info("Registered Rucio JupyterLab extension at URL path /rucio-jupyterlab")

    setup_logging()  # Will use RUCIO_JUPYTERLAB_LOGLEVEL or default to WARNING

    logger = logging.getLogger("rucio_jupyterlab")
    logger.info("Rucio JupyterLab server extension loaded.")


_load_jupyter_server_extension = load_jupyter_server_extension
