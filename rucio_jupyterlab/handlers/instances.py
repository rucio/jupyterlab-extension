import tornado
import json
from .base import RucioAPIHandler


class InstancesHandler(RucioAPIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    def get(self):
        instances = self.rucio_config.list_instances()
        self.finish(json.dumps(instances))
