import requests
from .utils import parse_timestamp


def authenticate_userpass(base_url, username, password, account=None, app_id=None):
    headers = {'X-Rucio-Account': account, 'X-Rucio-Username': username,
               'X-Rucio-Password': password, 'X-Rucio-AppID': app_id}
    response = requests.get(
        url=f'{base_url}/auth/userpass', headers=headers, verify=False)
    response_headers = response.headers

    auth_token = response_headers['X-Rucio-Auth-Token']
    expires = response_headers['X-Rucio-Auth-Token-Expires']
    expires = parse_timestamp(expires)

    return (auth_token, expires)
