import os
import json
import tornado
import rucio_jupyterlab.utils as utils
from .base import RucioAPIHandler


class FileBrowserHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def get(self):
        home = os.path.expanduser('~')
        path = self.get_query_argument('path', default='')
        path = os.path.expanduser(path)

        if not path:
            path = home
        if path[0] != '/' and path[0] != '~':
            path = os.path.join(home, path)

        if not os.path.exists(path):
            self.set_status(404)
            self.finish(json.dumps({'success': False}))
            return

        items = os.listdir(path)

        def items_mapper(item, _):
            full_path = os.path.join(path, item)
            item_type = 'file' if os.path.isfile(full_path) else 'dir'
            return dict(type=item_type, name=item, path=full_path)

        items = utils.map(items, items_mapper)

        def items_filter(item, _):
            return item['name'][0] != '.'

        items = utils.filter(items, items_filter)

        self.finish(json.dumps(items))
