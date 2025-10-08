# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json, os
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
    """
    Tests the GET handler for oidc with 'env' configuration.
    It should return the name of the environment variable, not fetch from DB.
    """
    # 1. Setup mocks
    mock_self = MockHandler()
    mock_self.get_query_argument = mocker.Mock(side_effect=lambda x: {
        'namespace': 'atlas',
        'type': 'oidc'
    }[x])

    # 2. Mock the rucio instance to return the 'env' configuration
    mock_instance = mocker.MagicMock()
    mock_instance.instance_config = {
        'oidc_auth': 'env',
        'oidc_env_name': 'OIDC_TOKEN'
    }
    mock_rucio = mocker.MagicMock()
    mock_rucio.for_instance.return_value = mock_instance
    mock_self.rucio = mock_rucio

    # 3. Mock the 'finish' method to capture and verify the output
    def finish_side_effect(output):
        # Assert that the output is the JSON object created inside the handler
        assert json.loads(output) == {'oidc_auth_source': 'OIDC_TOKEN'}

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    # --- Execute the handler method ---
    AuthConfigHandler.get(mock_self)

    # --- Assertions ---
    # Ensure the finish method was called exactly once
    mock_self.finish.assert_called_once()
    # Ensure the correct query arguments were requested
    mock_self.get_query_argument.assert_has_calls([mocker.call('namespace'), mocker.call('type')])


def test_get_auth_config_oidc_file(mocker):
    """
    Tests the GET handler for oidc with 'file' configuration.
    It should return the file path, not fetch from DB.
    """
    # 1. Setup mocks
    mock_self = MockHandler()
    mock_self.get_query_argument = mocker.Mock(side_effect=lambda x: {
        'namespace': 'atlas',
        'type': 'oidc'
    }[x])

    # 2. Mock the rucio instance to return the 'file' configuration
    mock_instance = mocker.MagicMock()
    mock_instance.instance_config = {
        'oidc_auth': 'file',
        'oidc_file_name': '/tmp/oidc_token'
    }
    mock_rucio = mocker.MagicMock()
    mock_rucio.for_instance.return_value = mock_instance
    mock_self.rucio = mock_rucio

    # 3. Mock the 'finish' method to capture and verify the output
    def finish_side_effect(output):
        # Assert that the output is the JSON object with the file path
        assert json.loads(output) == {'oidc_auth_source': '/tmp/oidc_token'}

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    # --- Execute the handler method ---
    AuthConfigHandler.get(mock_self)

    # --- Assertions ---
    mock_self.finish.assert_called_once()
    mock_self.get_query_argument.assert_has_calls([mocker.call('namespace'), mocker.call('type')])


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
    """
    Tests the PUT handler for OIDC, ensuring it handles file operations
    and returns a lifetime upon successful authentication.
    """
    # 1. Setup the test with the corrected helper
    mock_self, mock_db = _setup_put_test(mocker, auth_type='oidc')

    # 2. Mock external dependencies
    fixed_timestamp = 1735776000  # 2025-01-02 00:00:00 UTC
    mocker.patch('rucio_jupyterlab.handlers.auth_config.RucioAPI.authenticate', return_value=(None, fixed_timestamp))
    mocker.patch('rucio_jupyterlab.handlers.auth_config.RucioAPI.clear_auth_token_cache')

    # Mock filesystem and environment
    # CRITICAL FIX: Capture the mock object returned by patch()
    mock_isfile = mocker.patch('rucio_jupyterlab.handlers.auth_config.os.path.isfile', return_value=True)
    mocker.patch('os.environ', {}) # Mock os.environ as a dictionary
    mocked_open = mocker.patch('builtins.open', mocker.mock_open(read_data="secret-token-content"))

    # 3. Define the side effect for the 'finish' method to check the final output
    def finish_side_effect(output):
        response = json.loads(output)
        assert response['success'] is True
        assert response['lifetime'] == "2025-01-02T00:00:00Z"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    # --- Execute ---
    AuthConfigHandler.put(mock_self)

    # --- Assertions ---
    # Verify the database was updated
    mock_db.set_rucio_auth_credentials.assert_called_once_with(
        namespace=MOCK_ACTIVE_INSTANCE,
        auth_type='oidc',
        params={'token_path': '/fake/path/to/token.txt'}
    )

    # Verify filesystem interactions
    # CRITICAL FIX: Assert on the captured mock object
    mock_isfile.assert_called_once_with('/fake/path/to/token.txt')
    mocked_open.assert_called_once_with('/fake/path/to/token.txt', 'r')
    
    # Verify environment variable was set (based on setup helper)
    assert os.environ['OIDC_TOKEN'] == 'secret-token-content'

    # Verify finish was called
    mock_self.finish.assert_called_once()


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

    mock_db.set_rucio_auth_credentials = mocker.MagicMock()

    params = {'key': 'value'}
    if auth_type == 'oidc':
        params = {'token_path': '/fake/path/to/token.txt'}

    mocker.patch('rucio_jupyterlab.handlers.auth_config.get_db', return_value=mock_db)
    mocker.patch.object(mock_self, 'get_json_body', return_value={
        'namespace': MOCK_ACTIVE_INSTANCE,
        'type': auth_type,
        'params': params
    })

    mock_instance = mocker.MagicMock()
    mock_instance.instance_config = {
        'oidc_auth': 'env' if auth_type == 'oidc' else None,
        'oidc_env_name': 'OIDC_TOKEN'
    }

    mock_rucio = mocker.MagicMock()
    mock_rucio.for_instance.return_value = mock_instance
    mock_self.rucio = mock_rucio

    return mock_self, mock_db
