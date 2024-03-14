import json
from pathlib import Path

class ExtensionPaths:
    def __init__(self):
        self.HERE = Path(__file__).parent.parent
        self.package_data = self._load_package_data()

    def _load_package_data(self):
        package_path = self.HERE / "rucio_jupyterlab" / "labextension" / "package.json"
        with package_path.open() as fid:
            data = json.load(fid)
        return data

    def _jupyter_labextension_paths(self):
        return [{
            "src": "labextension",
            "dest": self.package_data["name"]
        }]

    def _jupyter_server_extension_paths(self):  # pragma: no cover
        return [{
            "module": "rucio_jupyterlab.server"
        }]

extension_paths = ExtensionPaths()