from prometheus_client import Counter, Summary
import functools

REQUEST_COUNT = Counter('my_jupyterlab_extension_requests_total', 'Total number of HTTP requests')
REQUEST_LATENCY = Summary('my_jupyterlab_extension_request_latency_seconds', 'Latency of HTTP requests')

def prometheus_metrics(handler_method):
    @functools.wraps(handler_method)
    def wrapper(self, *args, **kwargs):
        REQUEST_COUNT.inc()
        with REQUEST_LATENCY.time():
            return handler_method(self, *args, **kwargs)
    return wrapper