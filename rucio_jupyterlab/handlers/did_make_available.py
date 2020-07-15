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
