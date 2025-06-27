# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import json
import tornado
import logging
from rucio_jupyterlab.rucio.exceptions import RucioAPIException
from rucio_jupyterlab.mode_handlers.replica import ReplicaModeHandler
from rucio_jupyterlab.mode_handlers.download import DownloadModeHandler
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics

# Configure logging
logger = logging.getLogger(__name__)


class DIDMakeAvailableHandler(RucioAPIHandler):
    @tornado.web.authenticated
    @prometheus_metrics
    def post(self):
        logger.info("Received request to make DID available")
        namespace = self.get_query_argument('namespace')
        logger.debug("Namespace: %s", namespace)

        json_body = self.get_json_body()
        did = json_body['did']
        logger.debug("DID: %s", did)

        scope, name = did.split(':')
        logger.debug("Scope: %s, Name: %s", scope, name)

        rucio_instance = self.rucio.for_instance(namespace)
        mode = rucio_instance.instance_config.get('mode', 'replica')
        logger.debug("Mode: %s", mode)

        if mode == 'replica':
            handler = ReplicaModeHandler(namespace, rucio_instance)
            logger.debug("Using ReplicaModeHandler")
        elif mode == 'download':
            handler = DownloadModeHandler(namespace, rucio_instance)
            logger.debug("Using DownloadModeHandler")

        try:
            output = handler.make_available(scope, name)
            logger.info("Handler output: %s", output)
        except RucioAPIException as e:
            # Set the HTTP status from the exception, falling back to 500 if not present
            self.set_status(e.status_code or 500)

            # Finish the request with a detailed JSON error payload
            self.finish(json.dumps({
                'success': False,
                'error': e.message,
                'exception_class': e.exception_class,
                'exception_message': e.exception_message
            }))

        self.finish(json.dumps(output))
