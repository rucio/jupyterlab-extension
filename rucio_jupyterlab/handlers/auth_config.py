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
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.rucio import RucioAPI
from .base import RucioAPIHandler


class AuthConfigHandler(RucioAPIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        auth_type = self.get_query_argument('type')

        db = get_db()  # pylint: disable=invalid-name
        auth_credentials = db.get_rucio_auth_credentials(namespace=namespace, auth_type=auth_type)

        if auth_credentials:
            self.finish(json.dumps(auth_credentials))
        else:
            self.set_status(404)
            self.finish({'success': False, 'error': 'Auth credentials not set'})

    @tornado.web.authenticated
    def put(self):
        json_body = self.get_json_body()
        namespace = json_body['namespace']
        auth_type = json_body['type']
        params = json_body['params']

        db = get_db()  # pylint: disable=invalid-name
        db.set_rucio_auth_credentials(namespace=namespace, auth_type=auth_type, params=params)

        RucioAPI.clear_auth_token_cache()

        self.finish(json.dumps({'success': True}))
