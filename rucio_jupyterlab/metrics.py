from prometheus_client import Counter, Summary
import functools

REQUEST_COUNT = Counter('rucio_jupyterlab_requests_total', 'Total number of HTTP requests')
REQUEST_LATENCY = Summary('rucio_jupyterlab_request_latency_seconds', 'Latency of HTTP requests')

def prometheus_metrics(handler_method):
    @functools.wraps(handler_method)
    def wrapper(self, *args, **kwargs):
        REQUEST_COUNT.inc()
        with REQUEST_LATENCY.time():
            return handler_method(self, *args, **kwargs)
    return wrapper