# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json
from pathlib import Path

from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
    skip_if_exists
)
import setuptools

HERE = Path(__file__).parent.resolve()

# The name of the project
name = "rucio_jupyterlab"

lab_path = (HERE / name / "labextension")

# Representative files that should exist after a successful build
jstargets = [
    str(lab_path / "package.json"),
]

package_data_spec = {
    name: ["*"],
}

labext_name = "rucio-jupyterlab"

data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, str(lab_path), "**"),
    ("share/jupyter/labextensions/%s" % labext_name, str(HERE), "install.json"),
    ("etc/jupyter/jupyter_notebook_config.d", "jupyter-config/jupyter_notebook_config.d", "rucio_jupyterlab.json"),
    ("etc/jupyter/jupyter_server_config.d", "jupyter-config/jupyter_server_config.d", "rucio_jupyterlab.json"),
]

cmdclass = create_cmdclass("jsdeps",
    package_data_spec=package_data_spec,
    data_files_spec=data_files_spec
)

js_command = combine_commands(
    install_npm(HERE, build_cmd="build:prod", npm=["jlpm"]),
    ensure_targets(jstargets),
)

is_repo = (HERE / ".git").exists()
if is_repo:
    cmdclass["jsdeps"] = js_command
else:
    cmdclass["jsdeps"] = skip_if_exists(jstargets, js_command)

long_description = (HERE / "README.md").read_text()

# Get the package info from package.json
pkg_json = json.loads((HERE / "package.json").read_bytes())

setup_args = dict(
    name=name,
    version=pkg_json["version"],
    url=pkg_json["homepage"],
    author=pkg_json["author"]["name"],
    author_email=pkg_json["author"]["email"],
    description=pkg_json["description"],
    license=pkg_json["license"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    cmdclass=cmdclass,
    packages=setuptools.find_packages(),
    install_requires=[
        "jupyterlab~=3.0",
        "requests~=2.20",
        "peewee~=3.0",
        "jsonschema~=3.0",
        "psutil~=5.0",
        "rucio-clients~=1.0"
    ],
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.6",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab3"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Jupyter",
    ]
)


if __name__ == "__main__":
    setuptools.setup(**setup_args)
