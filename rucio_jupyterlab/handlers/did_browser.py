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
from rucio_jupyterlab.entity import AttachedFile
from rucio_jupyterlab.rucio.authenticators import RucioAuthenticationException
from .base import RucioAPIHandler


class DIDBrowserHandlerImpl:
    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name

    def get_files(self, scope, name, force_fetch=False):
        parent_did = f'{scope}:{name}'

        attached_files = self.db.get_attached_files(namespace=self.namespace, did=parent_did) if not force_fetch else None
        if attached_files:
            return [d.__dict__ for d in attached_files]

        file_dids = self.rucio.get_replicas(scope, name)
        attached_files = [AttachedFile(did=(d.get('scope') + ':' + d.get('name')), size=d.get('bytes')) for d in file_dids]
        self.db.set_attached_files(self.namespace, parent_did, attached_files)
        return [d.__dict__ for d in attached_files]


class DIDBrowserHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        poll = self.get_query_argument('poll', '0') == '1'
        did = self.get_query_argument('did')
        rucio = self.rucio.for_instance(namespace)
        (scope, name) = did.split(':')

        handler = DIDBrowserHandlerImpl(namespace, rucio)

        try:
            dids = handler.get_files(scope, name, poll)
            self.finish(json.dumps(dids))
        except RucioAuthenticationException:
            self.set_status(401)
            self.finish(json.dumps({'error': 'Authentication error '}))
