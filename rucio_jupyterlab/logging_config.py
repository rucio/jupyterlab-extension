# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import logging
import sys
from rucio_jupyterlab.config.config import RucioConfig, Config


def setup_logging(web_app):  # pragma: no cover
    """
    Sets up logging for the Rucio JupyterLab extension.
    This function configures the logging system to output messages to stdout
    with a specified format and log level.
    Parameters
    ----------
    web_app : jupyter_server.webapp.JupyterWebApplication
        The Jupyter web application instance, which contains the configuration settings.
    """

    rucio_config = RucioConfig(config=web_app.settings['config'])
    config = Config(rucio_config)

    logger = logging.getLogger("rucio_jupyterlab")
    if logger.hasHandlers():
        return  # Avoid adding multiple handlers

    level = config.get_log_level().upper()
    numeric_level = getattr(logging, level, logging.WARNING)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    logger.setLevel(numeric_level)
    handler.setLevel(numeric_level)
    logger.addHandler(handler)

    logger.info("Logging initialized at level: %s", level)
