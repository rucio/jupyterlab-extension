import tornado
import json
from .base import RucioAPIHandler
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile


class DIDBrowserHandler(RucioAPIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    def get(self):
        poll = self.get_query_argument('poll', '0') == '1'
        did = self.get_query_argument('did')
        (scope, name) = did.split(':')

        dids = self._get_files(scope, name, poll)
        self.finish(json.dumps(dids))

    def _get_files(self, scope, name, force_fetch=False):
        namespace = self.get_query_argument('namespace')
        rucio = self.rucio.for_instance(namespace)
        db = get_db()

        parent_did = f'{scope}:{name}'

        attached_files = db.get_attached_files(namespace=namespace, did=parent_did) if not force_fetch else None
        if attached_files:
            return [d.__dict__ for d in attached_files]
        else:
            file_dids = rucio.get_replicas(scope, name)
            attached_files = [AttachedFile(did=(d.get('scope') + ':' + d.get('name')), size=d.get('bytes')) for d in file_dids]
            db.set_attached_files(namespace, parent_did, attached_files)
            return [d.__dict__ for d in attached_files]
