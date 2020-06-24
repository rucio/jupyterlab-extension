from notebook.base.handlers import APIHandler   # pylint: disable=import-error


class RucioAPIHandler(APIHandler): # pragma: no cover
    def initialize(self, rucio_config, rucio, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.rucio_config = rucio_config
        self.rucio = rucio
