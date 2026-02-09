# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from jupyter_server.base.handlers import APIHandler, JupyterHandler   # pylint: disable=import-error
import concurrent.futures
from functools import partial
import tornado
from tornado.web import HTTPError
from rucio_jupyterlab.utils import ensure_credentials_present

# Create a global executor
MAX_WORKERS = 4
rucio_api_executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)

async def run_in_api_executor(func, *args, **kwargs):
    """
    Run a function in the Rucio API executor.
    :param func: The function to run.
    :param args: Positional arguments for the function.
    :param kwargs: Keyword arguments for the function.
    :return: The result of the function.
    """
    loop = tornado.ioloop.IOLoop.current()
    blocking_task = partial(func, *args, **kwargs)
    result = await loop.run_in_executor(rucio_api_executor, blocking_task)
    return result

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
 