# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

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
