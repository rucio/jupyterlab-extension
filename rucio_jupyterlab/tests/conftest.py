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
        "auth": {
            "type": "userpass",
            "username": MOCK_USERNAME,
            "password": MOCK_PASSWORD,
            "account": MOCK_ACCOUNT,
            "app_id": MOCK_APP_ID
        },
        "destination_rse": "SWAN-EOS",
        "rse_mount_path": "/eos/user/rucio",
        "path_begins_at": 4,
        "create_replication_rule_enabled": True,
        "direct_download_enabled": True
    }

    rucio_api = RucioAPI(instance_config)
    return rucio_api
