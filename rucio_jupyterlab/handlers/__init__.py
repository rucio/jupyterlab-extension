from notebook.utils import url_path_join
from .bookmarks import BookmarksHandler
from .instances import InstancesHandler
from .example import ExampleHandler
from rucio_jupyterlab.config import RucioConfig, Config


def setup_handlers(web_app):
    host_pattern = ".*$"

    rucio_config = RucioConfig(config=web_app.settings['config'])
    config = Config(rucio_config)

    handler_params = dict(rucio_config=config)

    base_url = web_app.settings["base_url"]
    base_path = url_path_join(base_url, 'rucio-jupyterlab')
    handlers = [
        (url_path_join(base_path, 'get_example'), ExampleHandler, handler_params),
        (url_path_join(base_path, 'instances'), InstancesHandler, handler_params),
        (url_path_join(base_path, 'bookmarks'), BookmarksHandler, handler_params)
    ]
    web_app.add_handlers(host_pattern, handlers)
