import json
import tornado
from rucio_jupyterlab.db import get_db
from .base import RucioAPIHandler


class AuthConfigHandler(RucioAPIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    def get(self):
        db = get_db()  # pylint: disable=invalid-name
        auth_credentials = db.get_rucio_auth_credentials()
        self.finish(json.dumps(auth_credentials))

    @tornado.web.authenticated
    def put(self):
        json_body = self.get_json_body()
        instance = json_body['instance']
        auth_type = json_body['type']
        params = json_body['params']

        db = get_db()  # pylint: disable=invalid-name
        db.set_rucio_auth_credentials(namespace=instance, auth_type=auth_type, params=params)

        self.finish(json.dumps({'success': True}))
