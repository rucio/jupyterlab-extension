import json
from pathlib import Path
import os

HERE = os.path.abspath(os.curdir)

# HERE = Path(__file__).parent.parent

with (HERE / "rucio_jupyterlab" / "labextension" / "package.json").open() as fid:
    data = json.load(fid)


def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": data["name"]
    }]


def _jupyter_server_extension_paths():  # pragma: no cover
    return [{
        "module": "rucio_jupyterlab.server"
    }]
