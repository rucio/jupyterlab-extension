import json
import tornado
from rucio_jupyterlab.db import get_db
from .base import RucioAPIHandler


class PurgeCacheHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def post(self):
        db = get_db()  # pylint: disable=invalid-name
        db.purge_cache()
        self.finish(json.dumps({'success': True}))
