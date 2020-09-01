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
from rucio_jupyterlab.mode_handlers.replica import ReplicaModeHandler
from rucio_jupyterlab.mode_handlers.download import DownloadModeHandler
from .base import RucioAPIHandler


class DIDMakeAvailableHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def post(self):
        namespace = self.get_query_argument('namespace')
        json_body = self.get_json_body()
        did = json_body['did']
        scope, name = did.split(':')

        rucio_instance = self.rucio.for_instance(namespace)
        mode = rucio_instance.instance_config.get('mode', 'replica')

        if mode == 'replica':
            handler = ReplicaModeHandler(namespace, rucio_instance)
        elif mode == 'download':
            handler = DownloadModeHandler(namespace, rucio_instance)

        try:
            output = handler.make_available(scope, name)
        except RucioAuthenticationException:
            self.set_status(401)
            output = {'error': 'Authentication error'}

        self.finish(json.dumps(output))
