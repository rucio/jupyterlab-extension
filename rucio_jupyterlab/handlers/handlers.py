# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from notebook.utils import url_path_join  # pylint: disable=import-error
from rucio_jupyterlab.config import RucioConfig, Config
from rucio_jupyterlab.rucio import RucioAPIFactory
from .instances import InstancesHandler
from .auth_config import AuthConfigHandler
from .did_browser import DIDBrowserHandler
from .did_search import DIDSearchHandler
from .did_details import DIDDetailsHandler
from .did_make_available import DIDMakeAvailableHandler
from .file_browser import FileBrowserHandler
from .purge_cache import PurgeCacheHandler


def setup_handlers(web_app):  # pragma: no cover
    host_pattern = ".*$"

    rucio_config = RucioConfig(config=web_app.settings['config'])
    config = Config(rucio_config)
    rucio_factory = RucioAPIFactory(config=config)

    handler_params = dict(rucio_config=config, rucio=rucio_factory)

    base_url = web_app.settings["base_url"]
    base_path = url_path_join(base_url, 'rucio-jupyterlab')
    handlers = [
        (url_path_join(base_path, 'instances'), InstancesHandler, handler_params),
        (url_path_join(base_path, 'auth'), AuthConfigHandler, handler_params),
        (url_path_join(base_path, 'files'), DIDBrowserHandler, handler_params),
        (url_path_join(base_path, 'did'), DIDDetailsHandler, handler_params),
        (url_path_join(base_path, 'did-search'), DIDSearchHandler, handler_params),
        (url_path_join(base_path, 'did', 'make-available'), DIDMakeAvailableHandler, handler_params),
        (url_path_join(base_path, 'file-browser'), FileBrowserHandler, handler_params),
        (url_path_join(base_path, 'purge-cache'), PurgeCacheHandler, handler_params)
    ]
    web_app.add_handlers(host_pattern, handlers)
