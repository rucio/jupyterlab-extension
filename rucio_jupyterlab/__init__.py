import json
from pathlib import Path
import os

HERE = Path(os.path.abspath(os.curdir)).parent
try:
    print("1st case; ", HERE)

    with (HERE / "labextension" / "package.json").open() as fid:
        data = json.load(fid)
except FileNotFoundError:
    HERE = HERE.parent
    print("2nd case; ", HERE)

    with (HERE / "labextension" / "package.json").open() as fid:
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
