# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import pytest
from jsonschema.exceptions import ValidationError
from rucio_jupyterlab.config import Config
from .mocks.mock_db import Struct


def test_config_init__local_config__replica_mode__schema_valid():
    mock_instances = [
        {
            "name": "atlas",
            "display_name": "ATLAS",
            "rucio_base_url": "https://rucio",
            "mode": "replica",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4
        }
    ]

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    assert config.get_instance_config('atlas') == mock_instances[0], "Invalid instances"


def test_config_init__local_config__replica_mode__schema_invalid():
    mock_instances = [
        {
            "display_name": "ATLAS",
            "rucio_base_url": "https://rucio",
            "mode": "replica",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4
        }
    ]

    mock_config = Struct(instances=mock_instances)

    with pytest.raises(ValidationError):
        Config(mock_config)


def test_config_init__local_config__download_mode__schema_valid():
    mock_instances = [
        {
            "name": "atlas",
            "display_name": "ATLAS",
            "rucio_base_url": "https://rucio",
            "mode": "download",
            "rucio_ca_cert": '/opt/rucio.pem'
        }
    ]

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    assert config.get_instance_config('atlas') == mock_instances[0], "Invalid instances"


def test_config_init__local_config__download_mode__schema_invalid():
    mock_instances = [
        {
            "display_name": "ATLAS",
            "rucio_base_url": "https://rucio",
            "mode": "download"
        }
    ]

    mock_config = Struct(instances=mock_instances)

    with pytest.raises(ValidationError):
        Config(mock_config)


def test_config_init__remote_config__schema_valid__no_overlapping_item(requests_mock):
    mock_instances = [
        {
            "name": "cms",
            "display_name": "CMS",
            "mode": "replica",
            "$url": "http://localhost/rucio.json"
        }
    ]

    mock_config = Struct(instances=mock_instances)

    remote_config = {
        "rucio_base_url": "https://rucio",
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1
    }

    requests_mock.get("http://localhost/rucio.json", json=remote_config)
    config = Config(mock_config)

    expected_config = {
        "name": "cms",
        "display_name": "CMS",
        "mode": "replica",
        "$url": "http://localhost/rucio.json",
        "rucio_base_url": "https://rucio",
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1
    }

    assert config.get_instance_config('cms') == expected_config, "Invalid remote config format"


def test_config_init__remote_config__schema_valid__overlapping_item(requests_mock):
    mock_instances = [
        {
            "name": "cms",
            "display_name": "CMS-Local",
            "mode": "replica",
            "$url": "http://localhost/rucio.json"
        }
    ]

    mock_config = Struct(instances=mock_instances)

    remote_config = {
        "display_name": "CMS-Remote",
        "rucio_base_url": "https://rucio",
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1
    }

    requests_mock.get("http://localhost/rucio.json", json=remote_config)
    config = Config(mock_config)

    expected_config = {
        "name": "cms",
        "display_name": "CMS-Local",
        "mode": "replica",
        "$url": "http://localhost/rucio.json",
        "rucio_base_url": "https://rucio",
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1
    }

    assert config.get_instance_config('cms') == expected_config, "Invalid remote config format"


def test_config_init__remote_config__schema_invalid(requests_mock):
    mock_instances = [
        {
            "name": "cms",
            "display_name": "CMS",
            "mode": "replica",
            "$url": "http://localhost/rucio.json"
        }
    ]

    mock_config = Struct(instances=mock_instances)

    remote_config = {
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1
    }

    requests_mock.get("http://localhost/rucio.json", json=remote_config)

    with pytest.raises(ValidationError):
        Config(mock_config)


def test_list_instances__oidc_disabled():
    mock_instances = [
        {
            "name": "atlas",
            "display_name": "ATLAS",
            "mode": "replica",
            "rucio_base_url": "https://rucio",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4
        },
        {
            "name": "cms",
            "display_name": "CMS",
            "mode": "replica",
            "rucio_base_url": "https://rucio-cms",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4
        }
    ]

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    expected_instances = [
        {'display_name': 'ATLAS', 'name': 'atlas', 'mode': 'replica', 'oidc_enabled': False, 'webui_url': None},
        {'display_name': 'CMS', 'name': 'cms', 'mode': 'replica', 'oidc_enabled': False, 'webui_url': None}
    ]

    assert config.list_instances() == expected_instances, "Invalid instances"


def test_list_instances__oidc_file__file_config_exists__file_exists__oidc_should_be_enabled(mocker):
    mock_instances = [
        {
            "name": "escape",
            "display_name": "ESCAPE",
            "mode": "replica",
            "rucio_base_url": "https://rucio-cms",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "oidc_auth": "file",
            "oidc_file_name": "/tmp/oauth2"
        }
    ]

    mocker.patch('rucio_jupyterlab.config.config.get_oidc_token', return_value='oauth2:token:resource')

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    expected_instances = [
        {'display_name': 'ESCAPE', 'name': 'escape', 'mode': 'replica', 'oidc_enabled': True, 'webui_url': None},
    ]

    assert config.list_instances() == expected_instances, "Invalid instances"


def test_list_instances__oidc_file__file_config_exists__file_does_not_exist__oidc_should_be_disabled(mocker):
    mock_instances = [
        {
            "name": "escape",
            "display_name": "ESCAPE",
            "mode": "replica",
            "rucio_base_url": "https://rucio-cms",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "oidc_auth": "file",
            "oidc_file_name": "/tmp/oauth2"
        }
    ]

    mocker.patch('rucio_jupyterlab.config.config.get_oidc_token', return_value=None)

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    expected_instances = [
        {'display_name': 'ESCAPE', 'name': 'escape', 'mode': 'replica', 'oidc_enabled': False, 'webui_url': None},
    ]

    assert config.list_instances() == expected_instances, "Invalid instances"


def test_list_instances__oidc_file__file_config_does_not_exist__oidc_should_be_disabled(mocker):
    mock_instances = [
        {
            "name": "escape",
            "display_name": "ESCAPE",
            "mode": "replica",
            "rucio_base_url": "https://rucio-cms",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "oidc_auth": "file",
        }
    ]

    mocker.patch('rucio_jupyterlab.config.config.get_oidc_token', return_value=None)

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    expected_instances = [
        {'display_name': 'ESCAPE', 'name': 'escape', 'mode': 'replica', 'oidc_enabled': False, 'webui_url': None},
    ]

    assert config.list_instances() == expected_instances, "Invalid instances"


def test_list_instances__oidc_env__env_config_exists__env_exists__oidc_should_be_enabled(mocker):
    mock_instances = [
        {
            "name": "escape",
            "display_name": "ESCAPE",
            "mode": "replica",
            "rucio_base_url": "https://rucio-cms",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "oidc_auth": "env",
            "oidc_env_name": "/tmp/oauth2"
        }
    ]

    mocker.patch('rucio_jupyterlab.config.config.get_oidc_token', return_value='oauth2:token:resource')

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    expected_instances = [
        {'display_name': 'ESCAPE', 'name': 'escape', 'mode': 'replica', 'oidc_enabled': True, 'webui_url': None},
    ]

    assert config.list_instances() == expected_instances, "Invalid instances"


def test_list_instances__oidc_env__env_config_exists__env_does_not_exist__oidc_should_be_disabled(mocker):
    mock_instances = [
        {
            "name": "escape",
            "display_name": "ESCAPE",
            "mode": "replica",
            "rucio_base_url": "https://rucio-cms",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "oidc_auth": "env",
            "oidc_env_name": "/tmp/oauth2"
        }
    ]

    mocker.patch('rucio_jupyterlab.config.config.get_oidc_token', return_value=None)

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    expected_instances = [
        {'display_name': 'ESCAPE', 'name': 'escape', 'mode': 'replica', 'oidc_enabled': False, 'webui_url': None},
    ]

    assert config.list_instances() == expected_instances, "Invalid instances"


def test_list_instances__oidc_env__env_config_does_not_exist__oidc_should_be_disabled(mocker):
    mock_instances = [
        {
            "name": "escape",
            "display_name": "ESCAPE",
            "mode": "replica",
            "rucio_base_url": "https://rucio-cms",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "oidc_auth": "env",
        }
    ]

    mocker.patch('rucio_jupyterlab.config.config.get_oidc_token', return_value=None)

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    expected_instances = [
        {'display_name': 'ESCAPE', 'name': 'escape', 'mode': 'replica', 'oidc_enabled': False, 'webui_url': None},
    ]

    assert config.list_instances() == expected_instances, "Invalid instances"


def test_list_instances__webui_config_exists__webui_url_should_be_correct(mocker):
    mock_instances = [
        {
            "name": "escape",
            "display_name": "ESCAPE",
            "mode": "replica",
            "rucio_base_url": "https://rucio-cms",
            "rucio_webui_url": "https://rucio-cms-webui",
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4
        }
    ]

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    expected_instances = [
        {'display_name': 'ESCAPE', 'name': 'escape', 'mode': 'replica', 'oidc_enabled': False, 'webui_url': 'https://rucio-cms-webui'},
    ]

    assert config.list_instances() == expected_instances, "Invalid instances"
