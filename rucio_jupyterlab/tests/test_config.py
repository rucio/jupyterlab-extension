import pytest
from jsonschema.exceptions import ValidationError
from rucio_jupyterlab.config import Config
from .mocks.mock_db import Struct


def test_config_init__local_config__schema_valid():
    mock_instances = [
        {
            "name": "atlas",
            "display_name": "ATLAS",
            "rucio_base_url": "https://rucio",
            "auth": {
                "type": "userpass",
                "username": "swan",
                "password": "swan",
                "account": "swan"
            },
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "create_replication_rule_enabled": True,
            "direct_download_enabled": True
        }
    ]

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    assert config.get_instance_config('atlas') == mock_instances[0], "Invalid instances"


def test_config_init__local_config__schema_invalid():
    mock_instances = [
        {
            "display_name": "ATLAS",
            "rucio_base_url": "https://rucio",
            "auth": {
                "type": "userpass",
                "username": "swan",
                "password": "swan",
                "account": "swan"
            },
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "create_replication_rule_enabled": True,
            "direct_download_enabled": True
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
            "$url": "http://localhost/rucio.json"
        }
    ]

    mock_config = Struct(instances=mock_instances)

    remote_config = {
        "rucio_base_url": "https://rucio",
        "auth": {
            "type": "userpass",
            "username": "swan",
            "password": "swan"
        },
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1,
        "create_replication_rule_enabled": True,
        "direct_download_enabled": True
    }

    requests_mock.get("http://localhost/rucio.json", json=remote_config)
    config = Config(mock_config)

    expected_config = {
        "name": "cms",
        "display_name": "CMS",
        "$url": "http://localhost/rucio.json",
        "rucio_base_url": "https://rucio",
        "auth": {
            "type": "userpass",
            "username": "swan",
            "password": "swan"
        },
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1,
        "create_replication_rule_enabled": True,
        "direct_download_enabled": True
    }

    assert config.get_instance_config('cms') == expected_config, "Invalid remote config format"


def test_config_init__remote_config__schema_valid__overlapping_item(requests_mock):
    mock_instances = [
        {
            "name": "cms",
            "display_name": "CMS-Local",
            "$url": "http://localhost/rucio.json"
        }
    ]

    mock_config = Struct(instances=mock_instances)

    remote_config = {
        "display_name": "CMS-Remote",
        "rucio_base_url": "https://rucio",
        "auth": {
            "type": "userpass",
            "username": "swan",
            "password": "swan"
        },
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1,
        "create_replication_rule_enabled": True,
        "direct_download_enabled": True
    }

    requests_mock.get("http://localhost/rucio.json", json=remote_config)
    config = Config(mock_config)

    expected_config = {
        "name": "cms",
        "display_name": "CMS-Local",
        "$url": "http://localhost/rucio.json",
        "rucio_base_url": "https://rucio",
        "auth": {
            "type": "userpass",
            "username": "swan",
            "password": "swan"
        },
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1,
        "create_replication_rule_enabled": True,
        "direct_download_enabled": True
    }

    assert config.get_instance_config('cms') == expected_config, "Invalid remote config format"


def test_config_init__remote_config__schema_invalid(requests_mock):
    mock_instances = [
        {
            "name": "cms",
            "display_name": "CMS",
            "$url": "http://localhost/rucio.json"
        }
    ]

    mock_config = Struct(instances=mock_instances)

    remote_config = {
        "rucio_base_url": "https://rucio",
        "auth": {
            "type": "userpass",
            "username": "swan",
            "password": "swan"
        },
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 1,
        "create_replication_rule_enabled": True,
        "direct_download_enabled": True
    }

    requests_mock.get("http://localhost/rucio.json", json=remote_config)

    with pytest.raises(ValidationError):
        Config(mock_config)


def test_list_instances():
    mock_instances = [
        {
            "name": "atlas",
            "display_name": "ATLAS",
            "rucio_base_url": "https://rucio",
            "auth": {
                "type": "userpass",
                "username": "swan",
                "password": "swan",
                "account": "swan"
            },
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "create_replication_rule_enabled": True,
            "direct_download_enabled": True
        },
        {
            "name": "cms",
            "display_name": "CMS",
            "rucio_base_url": "https://rucio-cms",
            "auth": {
                "type": "userpass",
                "username": "swan",
                "password": "swan",
                "account": "swan"
            },
            "destination_rse": "SWAN-EOS",
            "rse_mount_path": "/eos/user/rucio",
            "path_begins_at": 4,
            "create_replication_rule_enabled": True,
            "direct_download_enabled": True
        }
    ]

    mock_config = Struct(instances=mock_instances)
    config = Config(mock_config)

    expected_instances = [
        {'display_name': 'ATLAS', 'name': 'atlas'},
        {'display_name': 'CMS', 'name': 'cms'}
    ]

    assert config.list_instances() == expected_instances, "Invalid instances"
