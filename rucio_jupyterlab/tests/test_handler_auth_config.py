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

    mock_self.get_query_argument = mocker.Mock(side_effect=lambda x: {
        'namespace': MOCK_ACTIVE_INSTANCE,
        'type': MOCK_AUTH_TYPE
    }[x])

    mocker.patch('rucio_jupyterlab.handlers.auth_config.get_db', return_value=mock_db)
    mocker.patch.object(mock_db, 'get_active_auth_method', return_value=MOCK_AUTH_TYPE)
    mocker.patch.object(mock_db, 'get_rucio_auth_credentials', return_value=MOCK_AUTH_CREDENTIALS)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        assert finish_json == MOCK_AUTH_CREDENTIALS, "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    AuthConfigHandler.get(mock_self)


def test_get_auth_config_oidc_env(mocker):
    mock_self = MockHandler()
    mock_self.get_query_argument = mocker.Mock(side_effect=lambda x: {
        'namespace': 'atlas',
        'type': 'oidc'
    }[x])

    # Mock instance config for OIDC env
    mock_instance = mocker.MagicMock()
    mock_instance.instance_config = {
        'oidc_auth': 'env',
        'oidc_env_name': 'OIDC_TOKEN'
    }

    mock_rucio = mocker.MagicMock()
    mock_rucio.for_instance.return_value = mock_instance
    mock_self.rucio = mock_rucio

    def finish_side_effect(output):
        assert json.loads(output) == {'oidc_auth_source': 'OIDC_TOKEN'}

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    AuthConfigHandler.get(mock_self)


def test_get_auth_config_oidc_file(mocker):
    mock_self = MockHandler()
    mock_self.get_query_argument = mocker.Mock(side_effect=lambda x: {
        'namespace': 'atlas',
        'type': 'oidc'
    }[x])

    # Mock instance config for OIDC file
    mock_instance = mocker.MagicMock()
    mock_instance.instance_config = {
        'oidc_auth': 'file',
        'oidc_file_name': '/tmp/oidc_token'
    }

    mock_rucio = mocker.MagicMock()
    mock_rucio.for_instance.return_value = mock_instance
    mock_self.rucio = mock_rucio

    def finish_side_effect(output):
        assert json.loads(output) == {'oidc_auth_source': '/tmp/oidc_token'}

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    AuthConfigHandler.get(mock_self)


def test_put_instances(mocker):
    mock_self, mock_db = _setup_put_test(mocker, auth_type='userpass')
    # Convert to MagicMock for assertions
    mock_db.set_rucio_auth_credentials = mocker.MagicMock()

    # Patch authentication so it doesn't actually call anything
    mocker.patch('rucio_jupyterlab.handlers.auth_config.RucioAPI.authenticate', return_value=(None, None))
    mocker.patch('rucio_jupyterlab.handlers.auth_config.RucioAPI.clear_auth_token_cache', return_value=None)

    def finish_side_effect(output):
        response = json.loads(output)
        assert response['success'] is True

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    AuthConfigHandler.put(mock_self)

    # Check expected call
    mock_db.set_rucio_auth_credentials.assert_called_once_with(
        namespace=MOCK_ACTIVE_INSTANCE,
        auth_type='userpass',
        params={'key': 'value'}
    )


def test_put_returns_lifetime_for_x509(mocker):
    mock_self, mock_db = _setup_put_test(mocker, auth_type='x509_proxy')

    # Mock authentication response with fixed timestamp
    fixed_timestamp = 1735689600  # 2025-01-01 00:00:00 UTC
    mocker.patch(
        'rucio_jupyterlab.handlers.auth_config.RucioAPI.authenticate',
        return_value=(None, fixed_timestamp)
    )
    mocker.patch('rucio_jupyterlab.handlers.auth_config.RucioAPI.clear_auth_token_cache', return_value=None)

    def finish_side_effect(output):
        response = json.loads(output)
        assert response['success'] is True
        assert response['lifetime'] == "2025-01-01T00:00:00Z"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    AuthConfigHandler.put(mock_self)


def test_put_returns_lifetime_for_oidc(mocker):
    mock_self, mock_db = _setup_put_test(mocker, auth_type='oidc')

    fixed_timestamp = 1735776000  # 2025-01-02 00:00:00 UTC
    mocker.patch(
        'rucio_jupyterlab.handlers.auth_config.RucioAPI.authenticate',
        return_value=(None, fixed_timestamp)
    )
    mocker.patch('rucio_jupyterlab.handlers.auth_config.RucioAPI.clear_auth_token_cache', return_value=None)

    def finish_side_effect(output):
        response = json.loads(output)
        assert response['success'] is True
        assert response['lifetime'] == "2025-01-02T00:00:00Z"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    AuthConfigHandler.put(mock_self)


def test_put_handles_authentication_failure(mocker):
    mock_self, mock_db = _setup_put_test(mocker)

    # Simulate authentication failure
    class MockAuthException(Exception):
        pass

    mock_exception = MockAuthException("Invalid credentials")
    mock_exception.status_code = 401
    mock_exception.message = "Auth failed"
    mock_exception.exception_class = "AuthenticationError"
    mock_exception.exception_message = "Invalid token"

    mocker.patch(
        'rucio_jupyterlab.handlers.auth_config.RucioAPI.authenticate',
        side_effect=mock_exception
    )
    mocker.patch('rucio_jupyterlab.handlers.auth_config.RucioAPI.clear_auth_token_cache', return_value=None)

    def finish_side_effect(output):
        response = json.loads(output)
        assert response == {
            'success': False,
            'error': 'Auth failed',
            'exception_class': 'AuthenticationError',
            'exception_message': 'Invalid token'
        }

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    AuthConfigHandler.put(mock_self)


# Helper function for setup
def _setup_put_test(mocker, auth_type='userpass'):
    mock_self = MockHandler()
    mock_db = MockDatabaseInstance()

    mocker.patch('rucio_jupyterlab.handlers.auth_config.get_db', return_value=mock_db)
    mocker.patch.object(mock_self, 'get_json_body', return_value={
        'namespace': MOCK_ACTIVE_INSTANCE,
        'type': auth_type,
        'params': {'key': 'value'}
    })

    mock_instance = mocker.MagicMock()
    mock_instance.instance_config = {
        'oidc_auth': 'env' if auth_type == 'oidc' else None
    }

    mock_rucio = mocker.MagicMock()
    mock_rucio.for_instance.return_value = mock_instance
    mock_self.rucio = mock_rucio

    return mock_self, mock_db
