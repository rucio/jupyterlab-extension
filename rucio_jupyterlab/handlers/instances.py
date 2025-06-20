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
from rucio_jupyterlab.metrics import prometheus_metrics


class InstancesHandler(RucioAPIHandler):

    @tornado.web.authenticated  # Ensure user authentication first
    @prometheus_metrics         # Then increment the metrics
    def get(self):
        db = get_db()
        active_instance = db.get_active_instance()
        if not active_instance:
            active_instance = self.rucio_config.get_default_instance()

        auth_type = db.get_active_auth_method()
        if not auth_type:
            auth_type = self.rucio_config.get_default_auth_type()

        instances = self.rucio_config.list_instances()
        self.finish(json.dumps({
            'active_instance': active_instance,
            'auth_type': auth_type,
            'instances': instances
        }))

    @tornado.web.authenticated
    @prometheus_metrics
    def put(self):
        json_body = self.get_json_body()
        picked_instance = json_body['instance']
        picked_auth_type = json_body['auth']

        db = get_db()
        db.set_active_instance(picked_instance)
        db.set_active_auth_method(picked_auth_type)

        RucioAPI.clear_auth_token_cache()

        self.finish(json.dumps({'success': True}))
