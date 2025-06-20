# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import functools
from prometheus_client import Counter, Summary

REQUEST_COUNT = Counter('rucio_jupyterlab_requests_total', 'Total number of HTTP requests')
REQUEST_LATENCY = Summary('rucio_jupyterlab_request_latency_seconds', 'Latency of HTTP requests')


def prometheus_metrics(handler_method):
    @functools.wraps(handler_method)
    def wrapper(self, *args, **kwargs):
        REQUEST_COUNT.inc()
        with REQUEST_LATENCY.time():
            return handler_method(self, *args, **kwargs)
    return wrapper
