import pytest
from rucio_jupyterlab.rucio import RucioAPI

mock_base_url = "https://rucio/"
mock_username = "username"
mock_password = "password"
mock_account = "account"
mock_app_id = "app_id"
mock_auth_token = 'abcde_token_ghijk'

@pytest.fixture
def rucio():
    instance_config = {
        "name": "atlas",
        "display_name": "ATLAS",
        "rucio_base_url": mock_base_url,
        "auth": {
            "type": "userpass",
            "username": mock_username,
            "password": mock_password,
            "account": mock_account,
            "app_id": mock_app_id
        },
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 4,
        "create_replication_rule_enabled": True,
        "direct_download_enabled": True
    }

    rucio_api = RucioAPI(instance_config)
    return rucio_api