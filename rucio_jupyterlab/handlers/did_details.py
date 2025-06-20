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
import logging
from rucio_jupyterlab.rucio.exceptions import RucioAPIException
from rucio_jupyterlab.mode_handlers.replica import ReplicaModeHandler
from rucio_jupyterlab.mode_handlers.download import DownloadModeHandler
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics
import tornado

logger = logging.getLogger(__name__)


class DIDDetailsHandler(RucioAPIHandler):
    STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
    STATUS_REPLICATING = "REPLICATING"
    STATUS_OK = "OK"
    STATUS_STUCK = "STUCK"

    @tornado.web.authenticated
    @prometheus_metrics
    def get(self):
        namespace = self.get_query_argument('namespace')
        poll = self.get_query_argument('poll', '0') == '1'
        did = self.get_query_argument('did')
        scope, name = did.split(':')

        rucio_instance = self.rucio.for_instance(namespace)
        mode = rucio_instance.instance_config.get('mode', 'replica')

        if mode == 'replica':
            handler = ReplicaModeHandler(namespace, rucio_instance)
        elif mode == 'download':
            handler = DownloadModeHandler(namespace, rucio_instance)

        try:
            output = handler.get_did_details(scope, name, poll)
            self.finish(json.dumps(output))
        except RucioAPIException as e:
            # Log the exception details
            logger.error("RucioAPIException occurred: %s, Class: %s, Message: %s", e.message, e.exception_class, e.exception_message)
            # Set the HTTP status from the exception, falling back to 500 if not present
            self.set_status(e.status_code or 500)

            # Finish the request with a detailed JSON error payload
            self.finish(json.dumps({
                'success': False,
                'error': e.message,
                'exception_class': e.exception_class,
                'exception_message': e.exception_message
            }))
