import tornado
import json
from .base import RucioAPIHandler
from rucio_jupyterlab.db import get_namespaced_db


class DIDBrowserHandler(RucioAPIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    def get(self):
        did = self.get_query_argument('did')
        (scope, name) = did.split(':')

        dids = self._get_files(scope, name)
        self.finish(json.dumps(dids))

    def _get_files(self, scope, name):
        namespace = self.get_query_argument('namespace')
        rucio = self.rucio.for_instance(namespace)
        db = get_namespaced_db(namespace)

        parent_did = f'{scope}:{name}'

        cached_file_dids = db.get_cached_file_dids(parent_did)
        if cached_file_dids:
            return cached_file_dids
        else:
            file_dids = rucio.get_files(scope, name)
            output = [f"{d['scope']}:{d['name']}" for d in file_dids]
            db.set_cached_file_dids(parent_did, output)
            return output
