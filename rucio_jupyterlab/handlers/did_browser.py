import tornado
import json
from .base import RucioAPIHandler
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile


class DIDBrowserHandlerImpl:
    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio

    def get_files(self, scope, name, force_fetch=False):
        db = get_db()

        parent_did = f'{scope}:{name}'

        attached_files = db.get_attached_files(namespace=self.namespace, did=parent_did) if not force_fetch else None
        if attached_files:
            return [d.__dict__ for d in attached_files]
        else:
            file_dids = self.rucio.get_replicas(scope, name)
            attached_files = [AttachedFile(did=(d.get('scope') + ':' + d.get('name')), size=d.get('bytes')) for d in file_dids]
            db.set_attached_files(self.namespace, parent_did, attached_files)
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

        dids = handler.get_files(scope, name, poll)
        self.finish(json.dumps(dids))
