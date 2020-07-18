import json
import tornado
from rucio_jupyterlab.rucio.authenticators import RucioAuthenticationException
from rucio_jupyterlab.mode_handlers.replica import ReplicaModeHandler
from rucio_jupyterlab.mode_handlers.download import DownloadModeHandler
from .base import RucioAPIHandler


class DIDDetailsHandler(RucioAPIHandler):
    STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
    STATUS_REPLICATING = "REPLICATING"
    STATUS_OK = "OK"
    STATUS_STUCK = "STUCK"

    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        poll = self.get_query_argument('poll', '0') == '1'
        did = self.get_query_argument('did')
        scope, name = did.split(':')

        rucio_instance = self.rucio.for_instance(namespace)
        mode = rucio_instance.instance_config.get('mode', 'replica')

        if mode == 'replica':
            handler = ReplicaModeHandler(namespace, rucio_instance)
        elif mode == 'download':
            handler = DownloadModeHandler(namespace, rucio_instance)

        try:
            output = handler.get_did_details(scope, name, poll)
            self.finish(json.dumps(output))
        except RucioAuthenticationException:
            self.set_status(401)
            self.finish(json.dumps({'error': 'Authentication error '}))
