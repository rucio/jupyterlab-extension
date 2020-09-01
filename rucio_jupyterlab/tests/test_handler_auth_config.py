# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json
from rucio_jupyterlab.handlers.auth_config import AuthConfigHandler
from .mocks.mock_db import MockDatabaseInstance
from .mocks.mock_handler import MockHandler

MOCK_ACTIVE_INSTANCE = 'atlas'
MOCK_AUTH_TYPE = 'userpass'
MOCK_AUTH_CREDENTIALS = {
    'username': 'username',
    'password': 'password',
    'account': 'account'
}


def test_get_auth_config(mocker):
    mock_self = MockHandler()
    mock_db = MockDatabaseInstance()

    mocker.patch('rucio_jupyterlab.handlers.auth_config.get_db', return_value=mock_db)
    mocker.patch.object(mock_db, 'get_active_auth_method', return_value=MOCK_AUTH_TYPE)
    mocker.patch.object(mock_db, 'get_rucio_auth_credentials', return_value=MOCK_AUTH_CREDENTIALS)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        assert finish_json == MOCK_AUTH_CREDENTIALS, "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    AuthConfigHandler.get(mock_self)


def test_put_instances(mocker):
    mock_self = MockHandler()
    mock_db = MockDatabaseInstance()

    mocker.patch('rucio_jupyterlab.handlers.auth_config.get_db', return_value=mock_db)
    mocker.patch.object(mock_db, 'set_rucio_auth_credentials')
    mocker.patch.object(mock_self, 'get_json_body', return_value={'namespace': MOCK_ACTIVE_INSTANCE, 'type': 'userpass', 'params': MOCK_AUTH_CREDENTIALS})

    AuthConfigHandler.put(mock_self)

    mock_db.set_rucio_auth_credentials.assert_called_once_with(namespace=MOCK_ACTIVE_INSTANCE, auth_type='userpass', params=MOCK_AUTH_CREDENTIALS)   # pylint: disable=no-member
