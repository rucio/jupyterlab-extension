import json

from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join
import tornado
import os

from .bookmarks import BookmarksHandler

class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post, 
    # patch, put, delete, options) to ensure only authorized user can request the 
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": "This is /rucio-jupyterlab/get_example endpoint!" + os.getcwd()
        }))


def setup_handlers(web_app):
    host_pattern = ".*$"
    
    base_url = web_app.settings["base_url"]
    base_path = url_path_join(base_url, 'rucio-jupyterlab')
    handlers = [
        (url_path_join(base_path, 'get_example'), RouteHandler),
        (url_path_join(base_path, 'bookmarks'), BookmarksHandler)
    ]
    web_app.add_handlers(host_pattern, handlers)
