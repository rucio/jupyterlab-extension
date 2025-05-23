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


class RucioAuthenticationException(Exception):
    def __init__(self, response):
        self.status_code = getattr(response, 'status_code', None)
        self.reason = getattr(response, 'reason', 'Unknown')
        self.headers = getattr(response, 'headers', {})

        self.exception_class = self.headers.get('ExceptionClass', None)
        self.exception_message = self.headers.get('ExceptionMessage', None)
        self.message = self.exception_message or response.text if hasattr(response, 'text') else 'Unknown authentication error'

        super().__init__(f"Authentication failed: {self.status_code} {self.reason}. "
                         f"Message: {self.message}")

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
        raise RucioAuthenticationException(response)


def authenticate_x509(base_url, cert_path, key_path=None, account=None, vo=None, app_id=None, rucio_ca_cert=False):
    try:
        print("Starting authenticate_x509...")
        print(f"base_url: {base_url}")
        print(f"cert_path: {cert_path}")
        print(f"key_path: {key_path}")
        print(f"account: {account}")
        print(f"vo: {vo}")
        print(f"app_id: {app_id}")
        print(f"rucio_ca_cert: {rucio_ca_cert}")

        account = account if account != '' else None    # Empty string is considered None
        print(f"Processed account: {account}")

        headers = {'X-Rucio-Account': account, 'X-Rucio-VO': vo, 'X-Rucio-AppID': app_id}
        print(f"Initial headers: {headers}")
        headers = utils.remove_none_values(headers)
        print(f"Headers after removing None values: {headers}")

        cert = (cert_path, key_path)
        print(f"Certificate paths: {cert}")

        print("Sending request to Rucio server...")
        response = requests.get(url=f'{base_url}/auth/x509', headers=headers, cert=cert, verify=rucio_ca_cert)
        print(f"Response received. Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")

        response_headers = response.headers
        auth_token = response_headers.get('X-Rucio-Auth-Token', None)
        expires = response_headers.get('X-Rucio-Auth-Token-Expires', None)
        print(f"Auth token: {auth_token}")
        print(f"Token expiration (raw): {expires}")

        if not auth_token or not expires:
            print("Missing authentication token or expiration in response headers.")
            raise RucioAuthenticationException(response)

        expires = parse_timestamp(expires)
        print(f"Token expiration (parsed): {expires}")

        print("Authentication successful.")
        return (auth_token, expires)
    except Exception as e:
        print("An error occurred during x509 authentication.")
        traceback.print_exc()
        raise RucioAuthenticationException(response)
    
def authenticate_oidc(base_url, oidc_auth, oidc_auth_source, rucio_ca_cert=False):
    try:
        oidc_token = get_oidc_token(oidc_auth, oidc_auth_source)
        print("-------------------------------------------------")
        print(f"oidc_token: {oidc_token}")  # Debugging line
        print("-------------------------------------------------")
        headers = {'X-Rucio-Auth-Token': oidc_token}

        response = requests.get(url=f'{base_url}/auth/validate', headers=headers, verify=rucio_ca_cert)

        if response.status_code != 200:
            raise RucioAuthenticationException(response)

        jwt_payload = jwt.decode(oidc_token, options={"verify_signature": False})
        lifetime = jwt_payload['exp']

        return (jwt_payload.get('sub', None), lifetime)
    except:
        traceback.print_exc()
        raise RucioAuthenticationException(response)
