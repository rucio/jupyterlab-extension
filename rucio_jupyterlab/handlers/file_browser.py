# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import os
import json
import tornado
import rucio_jupyterlab.utils as utils
from .base import RucioAPIHandler


class FileBrowserHandlerImpl:
    @staticmethod
    def list_contents(path):
        home = os.path.expanduser('~')
        path = os.path.expanduser(path)

        if not path:
            path = home
        if path[0] != '/' and path[0] != '~':
            path = os.path.join(home, path)

        if not os.path.exists(path):
            return None

        items = os.listdir(path)

        def items_mapper(item, _):
            full_path = os.path.join(path, item)
            item_type = 'file' if os.path.isfile(full_path) else 'dir'
            return dict(type=item_type, name=item, path=full_path)

        items = utils.map(items, items_mapper)
        items = utils.filter(items, lambda x, _: x['name'][0] != '.')
        return items


class FileBrowserHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def get(self):
        path = self.get_query_argument('path', default='')
        items = FileBrowserHandlerImpl.list_contents(path)

        if items is None:
            self.set_status(404)
            self.finish(json.dumps({'success': False}))
            return

        self.finish(json.dumps(items))
