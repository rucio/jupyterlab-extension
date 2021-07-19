# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021

import traceback
import requests
import jwt
import rucio_jupyterlab.utils as utils
from .utils import parse_timestamp, get_oidc_token


class RucioAuthenticationException(BaseException):
    pass


def authenticate_userpass(base_url, username, password, account=None, vo=None, app_id=None, rucio_ca_cert=False):
    try:
        account = account if account != '' else None    # Empty string is considered None

        headers = {'X-Rucio-Account': account, 'X-Rucio-VO': vo, 'X-Rucio-Username': username, 'X-Rucio-Password': password, 'X-Rucio-AppID': app_id}
        headers = utils.remove_none_values(headers)

        response = requests.get(url=f'{base_url}/auth/userpass', headers=headers, verify=rucio_ca_cert)
        response_headers = response.headers

        auth_token = response_headers['X-Rucio-Auth-Token']
        expires = response_headers['X-Rucio-Auth-Token-Expires']
        expires = parse_timestamp(expires)

        return (auth_token, expires)
    except:
        traceback.print_exc()
        raise RucioAuthenticationException()


def authenticate_x509(base_url, cert_path, key_path=None, account=None, vo=None, app_id=None, rucio_ca_cert=False):
    try:
        account = account if account != '' else None    # Empty string is considered None

        headers = {'X-Rucio-Account': account, 'X-Rucio-VO': vo, 'X-Rucio-AppID': app_id}
        headers = utils.remove_none_values(headers)

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


def authenticate_oidc(base_url, oidc_auth, oidc_auth_source, rucio_ca_cert=False):
    try:
        oidc_token = get_oidc_token(oidc_auth, oidc_auth_source)
        headers = {'X-Rucio-Auth-Token': oidc_token}

        response = requests.get(url=f'{base_url}/accounts/whoami', headers=headers, verify=rucio_ca_cert)

        if response.status_code != 200:
            raise RucioAuthenticationException()

        jwt_payload = jwt.decode(oidc_token, options={"verify_signature": False})
        expires = jwt_payload['exp']

        return (oidc_token, expires)
    except:
        traceback.print_exc()
        raise RucioAuthenticationException()
