from notebook.base.handlers import APIHandler


class RucioAPIHandler(APIHandler):
    def initialize(self, rucio_config, rucio, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.rucio_config = rucio_config
        self.rucio = rucio
