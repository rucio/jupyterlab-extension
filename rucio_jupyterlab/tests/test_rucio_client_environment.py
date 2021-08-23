# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import os
from unittest.mock import patch, mock_open
from rucio_jupyterlab.rucio.client_environment import RucioClientEnvironment


def test_rucio_client_environment_write_temp_config_file__should_make_correct_directory(mocker):
    mock_config = {
        'rucio_host': 'https://rucio',
        'auth_host': 'https://rucio-auth',
        'auth_type': 'userpass',
        'username': 'ruciouser',
        'password': 'ruciopass',
        'account': 'root',
        'ca_cert': '/opt/certs/rucio.pem'
    }

    mocker.patch.object(os, 'makedirs', return_value=None)
    with patch("builtins.open", mock_open()) as mock_file:
        RucioClientEnvironment.write_temp_config_file('/path', mock_config)
        mock_file.assert_called_with(os.path.join('/path', 'etc', 'rucio.cfg'), 'w')
        os.makedirs.assert_called_once_with(os.path.join('/path', 'etc'), exist_ok=True)    # pylint: disable=no-member
