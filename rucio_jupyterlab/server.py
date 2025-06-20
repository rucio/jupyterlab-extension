# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import logging
from rucio_jupyterlab.handlers import setup_handlers
from rucio_jupyterlab.logging_config import setup_logging


def load_jupyter_server_extension(server_app):  # pragma: no cover
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app : jupyter_server.serverapp.ServerApp
        Jupyter Server application instance.
    """
    setup_handlers(server_app.web_app)
    server_app.log.info("Registered Rucio JupyterLab extension at URL path /rucio-jupyterlab")

    setup_logging(server_app.web_app)  # Will use the default value in the jupyter_server_config.json or default to INFO (see RucioConfig in rucio_jupyterlab.config.config)

    logger = logging.getLogger("rucio_jupyterlab")
    logger.info("Rucio JupyterLab server extension loaded.")
