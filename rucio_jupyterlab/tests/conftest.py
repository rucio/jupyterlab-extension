# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import pytest
from rucio_jupyterlab.rucio import RucioAPI

MOCK_BASE_URL = "https://rucio/"
MOCK_USERNAME = "username"
MOCK_PASSWORD = "password"
MOCK_ACCOUNT = "account"
MOCK_APP_ID = "app_id"
MOCK_AUTH_TOKEN = 'abcde_token_ghijk'


@pytest.fixture
def rucio():
    instance_config = {
        "name": "atlas",
        "display_name": "ATLAS",
        "rucio_base_url": MOCK_BASE_URL,
        "app_id": MOCK_APP_ID,
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 4,
        "mode": "replica",
        "rucio_ca_cert": "/rucio.crt"
    }

    mock_auth_type = 'userpass'
    mock_auth_config = {
        'username': MOCK_USERNAME,
        'password': MOCK_PASSWORD,
        'account': MOCK_ACCOUNT
    }
    rucio_api = RucioAPI(instance_config, auth_type=mock_auth_type, auth_config=mock_auth_config)
    return rucio_api
