from .handlers import setup_handlers


def _jupyter_server_extension_paths():  # pragma: no cover
    return [{
        "module": "rucio_jupyterlab.server"
    }]


def load_jupyter_server_extension(lab_app):  # pragma: no cover
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    lab_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_handlers(lab_app.web_app)
    lab_app.log.info("Registered Rucio JupyterLab extension at URL path /rucio-jupyterlab")
