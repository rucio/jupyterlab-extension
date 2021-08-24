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
from rucio_jupyterlab.rucio.authenticators import RucioAuthenticationException
from .base import RucioAPIHandler


class ListScopesHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        rucio = self.rucio.for_instance(namespace)

        try:
            scopes = rucio.get_scopes()
            self.finish(json.dumps(scopes))
        except RucioAuthenticationException:
            self.set_status(401)
            self.finish(json.dumps({'error': 'authentication_error'}))
