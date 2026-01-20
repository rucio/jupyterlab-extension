# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from jupyter_server.base.handlers import APIHandler, JupyterHandler   # pylint: disable=import-error
from tornado.web import HTTPError
from rucio_jupyterlab.utils import ensure_credentials_present

class RucioAPIHandler(APIHandler):  # pragma: no cover
    def initialize(self, rucio_config, rucio, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.rucio_config = rucio_config
        self.rucio = rucio

    async def prepare(self):
        await super().prepare()
        if self.request.path.endswith((
            "/instances",
            "/auth",
            "/oidc-auth-check",
        )):
            return

        instance = self.get_query_argument("namespace", default=None)
        if not instance:
            raise HTTPError(400, reason="Missing Rucio instance")
        ensure_credentials_present(self.rucio, instance)
    
    def write_error(self, status_code, **kwargs):
        message = self._reason or "Unknown error"
        self.set_header("Content-Type", "application/json")
        self.finish({
            "success": False,
            "error": message,
            "status": status_code,
        })

class RucioHandler(JupyterHandler):  # pragma: no cover
    def initialize(self, rucio_config, rucio, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.rucio_config = rucio_config
        self.rucio = rucio
