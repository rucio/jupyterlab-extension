import tornado
import json
from .base import RucioAPIHandler


class ExampleHandler(RucioAPIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": "This is /rucio-jupyterlab/get_example endpoint!"
        }))
