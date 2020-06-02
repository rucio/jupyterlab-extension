import tornado
import json
from .base import RucioAPIHandler
from rucio_jupyterlab.db import get_db


class InstancesHandler(RucioAPIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    def get(self):
        db = get_db()
        active_instance = db.get_config('instance')
        instances = self.rucio_config.list_instances()
        self.finish(json.dumps({
            'active_instance': active_instance,
            'instances': instances
        }))

    @tornado.web.authenticated
    def put(self):
        json_body = self.get_json_body()
        picked_instance = json_body['instance']

        db = get_db()
        db.put_config('instance', picked_instance)

        self.finish(json.dumps({ 'success': True }))
