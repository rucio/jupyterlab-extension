import tornado
import json
from .base import RucioAPIHandler
from rucio_jupyterlab.db import get_namespaced_db


class FileMakeAvailableHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def post(self):
        namespace = self.get_query_argument('namespace')
        json_body = self.get_json_body()
        did = json_body['did']
        method = json_body['method']
        scope, name = did.split(':')

        if method == 'replica':
            output = self.transfer_replica(namespace, scope, name)
        else:
            self.set_status(400)
            output = {'error': 'Unknown method'}

        self.finish(json.dumps(output))

    def transfer_replica(self, namespace, scope, name):
        rucio = self.rucio.for_instance(namespace)
        db = get_namespaced_db(namespace)

        dids = [{'scope': scope, 'name': name}]
        destination_rse = rucio.instance_config.get('destination_rse')
        return rucio.add_replication_rule(dids=dids, rse_expression=destination_rse, copies=1)
