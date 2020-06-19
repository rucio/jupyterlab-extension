import tornado
import json
from .base import RucioAPIHandler

class UnknownMethodException(Exception):
    pass

class DIDMakeAvailableHandlerImpl:
    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio

    def handle_make_available(self, did, method):
        scope, name = did.split(':')
        if method == 'replica':
            return self.transfer_replica(scope, name)
        else:
            raise UnknownMethodException()

    def transfer_replica(self, scope, name):
        dids = [{'scope': scope, 'name': name}]
        destination_rse = self.rucio.instance_config.get('destination_rse')
        return self.rucio.add_replication_rule(dids=dids, rse_expression=destination_rse, copies=1)


class DIDMakeAvailableHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def post(self):
        namespace = self.get_query_argument('namespace')
        json_body = self.get_json_body()
        did = json_body['did']
        method = json_body['method']

        rucio_instance = self.rucio.for_instance(namespace)
        handler = DIDMakeAvailableHandlerImpl(namespace, rucio_instance)

        try:
            output = handler.handle_make_available(did, method)
        except UnknownMethodException:
            self.set_status(400)
            output = {'error': 'Unknown method'}
        
        self.finish(json.dumps(output))