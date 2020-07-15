import traceback
import requests
from .utils import parse_timestamp


class RucioAuthenticationException(BaseException):
    pass


def authenticate_userpass(base_url, username, password, account=None, app_id=None, rucio_ca_cert=False):
    try:
        headers = {'X-Rucio-Account': account, 'X-Rucio-Username': username, 'X-Rucio-Password': password, 'X-Rucio-AppID': app_id}
        response = requests.get(
            url=f'{base_url}/auth/userpass', headers=headers, verify=rucio_ca_cert)
        response_headers = response.headers

        auth_token = response_headers['X-Rucio-Auth-Token']
        expires = response_headers['X-Rucio-Auth-Token-Expires']
        expires = parse_timestamp(expires)

        return (auth_token, expires)
    except:
        traceback.print_exc()
        raise RucioAuthenticationException()


def authenticate_x509(base_url, cert_path, key_path=None, account=None, app_id=None, rucio_ca_cert=False):
    try:
        account = account if account != '' else None    # Empty string is considered None

        headers = {'X-Rucio-Account': account, 'X-Rucio-AppID': app_id}
        cert = (cert_path, key_path)
        response = requests.get(url=f'{base_url}/auth/x509', headers=headers, cert=cert, verify=rucio_ca_cert)
        response_headers = response.headers

        auth_token = response_headers['X-Rucio-Auth-Token']
        expires = response_headers['X-Rucio-Auth-Token-Expires']
        expires = parse_timestamp(expires)

        return (auth_token, expires)
    except:
        traceback.print_exc()
        raise RucioAuthenticationException()
