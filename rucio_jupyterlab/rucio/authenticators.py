# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021  
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import logging
import requests
import jwt
from rucio_jupyterlab import utils
from .utils import parse_timestamp, get_oidc_token

# Setup logging
logger = logging.getLogger(__name__)


class RucioAuthenticationException(Exception):
    def __init__(self, response):
        if isinstance(response, str):
            logger.debug(f"RucioAuthenticationException initialized with string response: {response}")
            self.status_code = None
            self.reason = 'Unknown'
            self.headers = {}
            self.exception_class = None
            self.exception_message = None
            self.message = response
        else:
            self.status_code = getattr(response, 'status_code', None)
            self.reason = getattr(response, 'reason', 'Unknown')
            self.headers = getattr(response, 'headers', {})
            self.exception_class = self.headers.get('ExceptionClass', None)
            self.exception_message = self.headers.get('ExceptionMessage', None)
            self.message = self.exception_message or (response.text if hasattr(response, 'text') else 'Unknown authentication error')

        super().__init__(f"Authentication failed: {self.status_code} {self.reason}. "
                         f"Message: {self.message}")

def authenticate_userpass(base_url, username, password, account=None, vo=None, app_id=None, rucio_ca_cert=False):
    response = None  # predefine response to avoid UnboundLocalError

    try:
        account = account if account != '' else None

        headers = {
            'X-Rucio-Account': account,
            'X-Rucio-VO': vo,
            'X-Rucio-Username': username,
            'X-Rucio-Password': password,
            'X-Rucio-AppID': app_id
        }
        headers = utils.remove_none_values(headers)

        logger.debug(f"Sending userpass authentication request to {base_url}/auth/userpass with headers: {headers}")

        response = requests.get(
            url=f'{base_url}/auth/userpass',
            headers=headers,
            verify=rucio_ca_cert
        )

        response.raise_for_status()  # raises requests.exceptions.HTTPError for status_code >= 400

        response_headers = response.headers
        auth_token = response_headers['X-Rucio-Auth-Token']
        expires = parse_timestamp(response_headers['X-Rucio-Auth-Token-Expires'])

        logger.debug("Userpass authentication successful.")
        return (auth_token, expires)
    
    except requests.exceptions.HTTPError as e:
        logger.debug(f"HTTP error during userpass authentication: {e.response.status_code} {e.response.reason}")
        logger.exception("HTTP error during userpass authentication.")
        raise RucioAuthenticationException(e.response)

    except requests.exceptions.RequestException as e:
        logger.debug(f"Request failed during userpass authentication: {str(e)}")
        logger.exception("Request failed during userpass authentication.")
        raise RucioAuthenticationException(str(e))

    except Exception as e:
        logger.exception("Unexpected error during userpass authentication.")
        # fallback: may still raise with partial response
        raise RucioAuthenticationException(response if response is not None else str(e))


def authenticate_x509(base_url, cert_path, key_path=None, account=None, vo=None, app_id=None, rucio_ca_cert=False):
    response = None  # predefine response to avoid UnboundLocalError

    try:
        logger.debug("Starting x509 authentication...")
        logger.debug(f"base_url: {base_url}, cert_path: {cert_path}, key_path: {key_path}, account: {account}, vo: {vo}, app_id: {app_id}, rucio_ca_cert: {rucio_ca_cert}")

        account = account if account != '' else None
        headers = {
            'X-Rucio-Account': account,
            'X-Rucio-VO': vo,
            'X-Rucio-AppID': app_id
        }
        headers = utils.remove_none_values(headers)
        cert = (cert_path, key_path)

        logger.debug(f"Sending x509 request with headers: {headers}, cert: {cert}")

        response = requests.get(
            url=f'{base_url}/auth/x509',
            headers=headers,
            cert=cert,
            verify=rucio_ca_cert)

        response.raise_for_status()  # raises requests.exceptions.HTTPError for status_code >= 400

        logger.debug(f"Response received. Status code: {response.status_code}, headers: {response.headers}")

        auth_token = response.headers.get('X-Rucio-Auth-Token')
        expires = response.headers.get('X-Rucio-Auth-Token-Expires')

        if not auth_token or not expires:
            logger.warning("Missing authentication token or expiration in x509 response headers.")
            raise RucioAuthenticationException(response)

        expires = parse_timestamp(expires)
        logger.debug(f"x509 authentication successful. Token expires at: {expires}")
        return (auth_token, expires)
    
    except requests.exceptions.HTTPError as e:
        logger.exception("HTTP error during x509 authentication.")
        raise RucioAuthenticationException(e.response)

    except requests.exceptions.RequestException as e:
        logger.exception("Request failed during x509 authentication.")
        raise RucioAuthenticationException(str(e))

    except Exception as e:
        logger.exception("Unexpected error during x509 authentication.")
        # fallback: may still raise with partial response
        raise RucioAuthenticationException(response if response is not None else str(e))


def authenticate_oidc(base_url, oidc_auth, oidc_auth_source, rucio_ca_cert=False):
    response = None  # predefine response to avoid UnboundLocalError

    try:
        logger.debug("Starting OIDC authentication...")
        oidc_token = get_oidc_token(oidc_auth, oidc_auth_source)
        headers = {'X-Rucio-Auth-Token': oidc_token}

        logger.debug(f"Sending OIDC validation request to {base_url}/auth/validate")

        response = requests.get(
            url=f'{base_url}/auth/validate',
            headers=headers,
            verify=rucio_ca_cert)
        
        response.raise_for_status()  # raises requests.exceptions.HTTPError for status_code >= 400

        if response.status_code != 200:
            logger.warning(f"OIDC token validation failed with status: {response.status_code}")
            raise RucioAuthenticationException(response)

        jwt_payload = jwt.decode(oidc_token, options={"verify_signature": False})
        lifetime = jwt_payload['exp']

        logger.debug(f"OIDC authentication successful. Token subject: {jwt_payload.get('sub')}, expires at: {lifetime}")
        return (jwt_payload.get('sub', None), lifetime)
    except requests.exceptions.HTTPError as e:
        logger.exception("HTTP error during OIDC authentication.")
        raise RucioAuthenticationException(e.response)

    except requests.exceptions.RequestException as e:
        logger.exception("Request failed during OIDC authentication.")
        raise RucioAuthenticationException(str(e))

    except Exception as e:
        logger.exception("Unexpected error during OIDC authentication.")
        # fallback: may still raise with partial response
        raise RucioAuthenticationException(response if response is not None else str(e))
