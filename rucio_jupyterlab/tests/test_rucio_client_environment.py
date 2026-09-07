# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import os
import pytest
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


def _make_env(rucio, tmp_path):
    instance = RucioClientEnvironment.__new__(RucioClientEnvironment)
    instance.rucio = rucio
    instance.instance_config = {}
    instance.base_url = 'https://rucio'
    instance.auth_config = None
    instance.auth_type = 'oidc'
    instance.auth_url = 'https://rucio-auth'
    instance.tempdir = None
    return instance


def test_prepare_oidc_authentication__writes_token_and_sets_env_var(mocker, tmp_path):
    rucio = mocker.Mock()
    rucio._get_auth_token.return_value = 'my-oidc-token'
    env = _make_env(rucio, tmp_path)
    mocker.patch.dict(os.environ, {}, clear=False)

    env.prepare_oidc_authentication(str(tmp_path))

    token_file_path = os.path.join(str(tmp_path), 'bearer_token')
    assert os.environ['BEARER_TOKEN_FILE'] == token_file_path
    with open(token_file_path) as f:
        assert f.read() == 'my-oidc-token'


def test_prepare_oidc_authentication__no_token_raises_and_does_not_set_env_var(mocker, tmp_path):
    rucio = mocker.Mock()
    rucio._get_auth_token.return_value = None
    env = _make_env(rucio, tmp_path)
    os.environ.pop('BEARER_TOKEN_FILE', None)

    with pytest.raises(RuntimeError, match='No OIDC token available'):
        env.prepare_oidc_authentication(str(tmp_path))

    assert 'BEARER_TOKEN_FILE' not in os.environ
    assert not os.path.exists(os.path.join(str(tmp_path), 'bearer_token'))


def test_prepare_oidc_authentication__auth_token_exception_propagates(mocker, tmp_path):
    rucio = mocker.Mock()
    rucio._get_auth_token.side_effect = RuntimeError('cannot authenticate')
    env = _make_env(rucio, tmp_path)
    os.environ.pop('BEARER_TOKEN_FILE', None)

    with pytest.raises(RuntimeError, match='Could not obtain an OIDC token'):
        env.prepare_oidc_authentication(str(tmp_path))

    assert 'BEARER_TOKEN_FILE' not in os.environ


def test_enter__oidc_token_failure_fails_setup_and_cleans_up_tempdir(mocker):
    rucio = mocker.Mock()
    rucio.instance_config = {}
    rucio.base_url = 'https://rucio'
    rucio.auth_config = None
    rucio.auth_type = 'oidc'
    rucio.auth_url = 'https://rucio-auth'
    rucio._get_auth_token.return_value = None

    env = RucioClientEnvironment(rucio)

    with pytest.raises(RuntimeError, match='No OIDC token available'):
        env.__enter__()

    # Setup failure must clean up after itself rather than leaving a stale RUCIO_HOME.
    assert env.tempdir is None or not os.path.exists(env.tempdir.name)
