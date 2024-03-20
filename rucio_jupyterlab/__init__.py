# import json
# from pathlib import Path
# #import os

# HERE = Path(__file__).parent.resolve()
# with (HERE / "labextension" / "package.json").open() as fid:
#         data = json.load(fid)

# try:
#     print("1st case; ", HERE)

#     with (HERE / "labextension" / "package.json").open() as fid:
#         data = json.load(fid)
# except FileNotFoundError:
#     HERE = HERE.parent
#     print("2nd case; ", HERE)

#     with (HERE / "labextension" / "package.json").open() as fid:
#         data = json.load(fid)    

try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings
    warnings.warn("Importing 'engarcia_py_package_name' outside a proper installation.")
    __version__ = "dev"

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "rucio-jupyterlab"
    }]


def _jupyter_server_extension_paths():  # pragma: no cover
    return [{
        "module": "rucio_jupyterlab.server"
    }]
