import tornado
import json
from .base import RucioAPIHandler
from rucio_jupyterlab.db import get_namespaced_db


class BookmarksHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        instance = get_namespaced_db(namespace)

        bookmarks = instance.get_bookmark().dicts()
        bookmark_dicts = []
        for bookmark in bookmarks:
            bookmark_dicts.append(bookmark)
        self.finish(json.dumps(bookmark_dicts))

    @tornado.web.authenticated
    def post(self):
        json_body = self.get_json_body()
        namespace = json_body['instance']
        did = json_body['did']
        did_type = json_body['did_type']

        instance = get_namespaced_db(namespace)
        instance.insert_bookmark(did, did_type)
        self.finish(json.dumps({'success': True}))

    @tornado.web.authenticated
    def delete(self):
        json_body = self.get_json_body()
        namespace = json_body['instance']
        did = json_body['did']

        instance = get_namespaced_db(namespace)
        instance.delete_bookmark(did)
        self.finish(json.dumps({'success': True}))
