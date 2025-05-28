# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import logging
import os
import sys

def setup_logging(level: str = None):
    logger = logging.getLogger("rucio_jupyterlab")
    if logger.hasHandlers():
        return  # Avoid adding multiple handlers

    level = level or os.environ.get("RUCIO_JUPYTERLAB_LOGLEVEL", "WARNING").upper()
    numeric_level = getattr(logging, level, logging.WARNING)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    logger.setLevel(numeric_level)
    handler.setLevel(numeric_level)
    logger.addHandler(handler)

    logger.propagate = False

    logger.debug(f"Logging initialized at level: {level}")
