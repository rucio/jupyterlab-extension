# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import os
import json

HOME = '/home/jovyan'


def write_jupyterlab_config():
    file_path = HOME + '/.jupyter/jupyter_notebook_config.json'
    if not os.path.isfile(file_path):
        os.makedirs(HOME + '/.jupyter/', exist_ok=True)
    else:
        config_file = open(file_path, 'r')
        config_payload = config_file.read()
        config_file.close()

    try:
        config_json = json.loads(config_payload)
    except:
        config_json = {}

    instance_config = {
        "name": os.getenv('RUCIO_NAME', "default"),
        "display_name": os.getenv('RUCIO_DISPLAY_NAME', "Default Instance"),
        "rucio_base_url": os.getenv('RUCIO_BASE_URL'),
        "rucio_auth_url": os.getenv('RUCIO_AUTH_URL'),
        "rucio_ca_cert": os.getenv('RUCIO_CA_CERT'),
        "site_name": os.getenv('RUCIO_SITE_NAME'),
        "vo": os.getenv('RUCIO_VO'),
        "voms_enabled": os.getenv('RUCIO_VOMS_ENABLED', '0') == '1',
        "voms_vomses_path": os.getenv('RUCIO_VOMS_VOMSES_PATH'),
        "voms_certdir_path": os.getenv('RUCIO_VOMS_CERTDIR_PATH'),
        "voms_vomsdir_path": os.getenv('RUCIO_VOMS_VOMSDIR_PATH'),
        "destination_rse": os.getenv('RUCIO_DESTINATION_RSE'),
        "rse_mount_path": os.getenv('RUCIO_RSE_MOUNT_PATH'),
        "path_begins_at": int(os.getenv('RUCIO_PATH_BEGINS_AT', '0')),
        "mode": os.getenv('RUCIO_MODE', 'replica'),
        "wildcard_enabled": os.getenv('RUCIO_WILDCARD_ENABLED', '0') == '1'
    }

    instance_config = {k: v for k, v in instance_config.items() if v is not None}
    config_json['RucioConfig'] = {
        'instances': [instance_config]
    }

    config_file = open(file_path, 'w')
    config_file.write(json.dumps(config_json, indent=2))
    config_file.close()


def write_ipython_config():
    file_path = HOME + '/.ipython/profile_default/ipython_kernel_config.json'
    extension_module = 'rucio_jupyterlab.kernels.ipython'

    if not os.path.isfile(file_path):
        os.makedirs(HOME + '/.ipython/profile_default/', exist_ok=True)
    else:
        config_file = open(file_path, 'r')
        config_payload = config_file.read()
        config_file.close()

    try:
        config_json = json.loads(config_payload)
    except:
        config_json = {}

    if 'IPKernelApp' not in config_json:
        config_json['IPKernelApp'] = {}

    ipkernel_app = config_json['IPKernelApp']

    if 'extensions' not in ipkernel_app:
        ipkernel_app['extensions'] = []

    if extension_module not in ipkernel_app['extensions']:
        ipkernel_app['extensions'].append(extension_module)

    config_file = open(file_path, 'w')
    config_file.write(json.dumps(config_json, indent=2))
    config_file.close()


if __name__ == '__main__':
    write_jupyterlab_config()
    write_ipython_config()
