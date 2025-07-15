# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json
import tornado
from rucio_jupyterlab.rucio.exceptions import RucioAPIException
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics


class ListScopesHandler(RucioAPIHandler):
    """
    Handler for retrieving the list of scopes from a Rucio instance.

    This handler processes GET requests to fetch the scopes associated with a specific namespace.
    It requires the user to be authenticated and tracks metrics using Prometheus.

    Methods:
        get():
            Handles the GET request to retrieve scopes. Expects a 'namespace' query parameter
            to identify the Rucio instance. Returns a JSON response containing the list of scopes
            or an error message in case of authentication failure.

    Raises:
        RucioAuthenticationException:
            If authentication fails, the handler responds with a 401 status code and an error message.
    """
    @tornado.web.authenticated
    @prometheus_metrics
    def get(self):
        namespace = self.get_query_argument('namespace')
        rucio = self.rucio.for_instance(namespace)

        try:
            scopes = rucio.get_scopes()
            self.finish(json.dumps({'success': True, 'scopes': scopes}))
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
