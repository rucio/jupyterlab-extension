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
import os
import errno
from rucio_jupyterlab import utils
from rucio_jupyterlab.rucio.utils import parse_timestamp, get_oidc_token
from rucio_jupyterlab.rucio.exceptions import RucioAuthenticationException, RucioRequestsException, RucioHTTPException

# Setup logging
logger = logging.getLogger(__name__)


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

        logger.debug("Sending userpass authentication request to %s/auth/userpass", base_url)
        logger.debug("Rucio CA path: %s", rucio_ca_cert)
        logger.debug("Headers: %s", headers)

        response = requests.get(
            url=f'{base_url}/auth/userpass',
            headers=headers,
            verify=rucio_ca_cert
        )

        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Headers: {response.headers}")

        response.raise_for_status()  # raises HTTPError for bad status codes

        response_headers = response.headers
        auth_token = response_headers['X-Rucio-Auth-Token']
        expires = parse_timestamp(response_headers['X-Rucio-Auth-Token-Expires'])

        logger.debug("Userpass authentication successful.")
        return (auth_token, expires)

    except requests.exceptions.HTTPError as e:
        logger.debug("HTTP error during userpass authentication: %s %s", e.response.status_code, e.response.reason)
        logger.error("Request error during authentication for %s: %s", "userpass", e)
        raise RucioHTTPException(e.response) from e

    except requests.exceptions.RequestException as e:
        logger.debug("Request failed during userpass authentication: %s", e)
        logger.error("Request error during authentication for %s: %s", "userpass", e)
        raise RucioRequestsException(str(e)) from e

    except Exception as e:
        logger.error("Unexpected error during authentication for %s: %s", "userpass", e)
        if response is not None:
            logger.error("Partial response received: status code %s, content: %s", response.status_code, response.text)
        else:
            logger.error("No response received.")
        raise RucioAuthenticationException(response, fallback_msg=str(e)) from e


def authenticate_x509(base_url, cert_path, key_path=None, account=None, vo=None, app_id=None, rucio_ca_cert=False):
    response = None  # predefine response to avoid UnboundLocalError

    try:
        logger.debug("Starting x509 authentication...")
        logger.debug("base_url: %s, cert_path: %s, key_path: %s, account: %s, vo: %s, app_id: %s, rucio_ca_cert: %s", base_url, cert_path, key_path, account, vo, app_id, rucio_ca_cert)

        if not cert_path:
            logger.error("cert_path must be provided for x509 authentication")
            raise ValueError("cert_path must be provided for x509 authentication")
        if not key_path:
            key_path = cert_path  # Use cert_path as key_path if not provided

        if not os.path.exists(cert_path):
            raise FileNotFoundError(errno.ENOENT, "File not found during x509 authentication: " + os.strerror(errno.ENOENT), cert_path)
        if not os.path.exists(key_path):
            raise FileNotFoundError(errno.ENOENT, "File not found during x509 authentication: " + os.strerror(errno.ENOENT), key_path)

        account = account if account != '' else None
        headers = {
            'X-Rucio-Account': account,
            'X-Rucio-VO': vo,
            'X-Rucio-AppID': app_id
        }
        headers = utils.remove_none_values(headers)
        cert = (cert_path, key_path)

        logger.debug("Sending x509 authentication request to %s/auth/x509", base_url)
        logger.debug("Certificate path: %s", cert)
        logger.debug("Headers: %s", headers)

        response = requests.get(
            url=f'{base_url}/auth/x509',
            headers=headers,
            cert=cert,
            verify=rucio_ca_cert)

        response.raise_for_status()  # raises requests.exceptions.HTTPError for status_code >= 400

        logger.debug("Response received. Status code: %s, headers: %s", response.status_code, response.headers)

        auth_token = response.headers.get('X-Rucio-Auth-Token')
        expires = response.headers.get('X-Rucio-Auth-Token-Expires')

        if not auth_token or not expires:
            logger.warning("Missing authentication token or expiration in x509 response headers.")
            raise RucioAuthenticationException(response)

        expires = parse_timestamp(expires)
        logger.debug("x509 authentication successful. Token expires at: %s", expires)
        return (auth_token, expires)

    except requests.exceptions.HTTPError as e:
        logger.error("Request error during authentication for %s: %s", "x509", e)
        raise RucioHTTPException(e.response)
    except requests.exceptions.RequestException as e:
        logger.error("Request error during authentication for %s: %s", "x509", e)
        raise RucioRequestsException(str(e))
    except FileNotFoundError as e:
        logger.error("File not found during authentication for %s: %s", "x509", e)
        raise FileNotFoundError(e)
    except Exception as e:
        logger.error("Unexpected error during authentication for %s: %s", "x509", e)
        raise RucioAuthenticationException(response, fallback_msg=str(e)) from e


def authenticate_oidc(base_url, oidc_auth, oidc_auth_source, rucio_ca_cert=False):
    response = None  # predefine response to avoid UnboundLocalError

    try:
        logger.debug("Starting OIDC authentication...")
        oidc_token = get_oidc_token(oidc_auth, oidc_auth_source)
        headers = {'X-Rucio-Auth-Token': oidc_token}

        logger.debug("Sending OIDC validation request to %s/auth/validate", base_url)

        response = requests.get(
            url=f'{base_url}/auth/validate',
            headers=headers,
            verify=rucio_ca_cert)

        response.raise_for_status()  # raises requests.exceptions.HTTPError for status_code >= 400

        if response.status_code != 200:
            logger.warning("OIDC token validation failed with status: %s", response.status_code)
            raise RucioAuthenticationException(response)

        jwt_payload = jwt.decode(oidc_token, options={"verify_signature": False})
        lifetime = jwt_payload['exp']

        logger.debug("OIDC authentication successful. Token subject: %s, expires at: %s", jwt_payload.get('sub'), lifetime)
        return (oidc_token, lifetime)
    except requests.exceptions.HTTPError as e:
        logger.error("Request error during authentication for %s: %s", "oidc", e)
        raise RucioHTTPException(e.response)

    except requests.exceptions.RequestException as e:
        logger.error("Request error during authentication for %s: %s", "oidc", e)
        raise RucioRequestsException(str(e))

    except Exception as e:
        logger.error("Unexpected error during authentication for %s: %s", "oidc", e)
        # fallback: may still raise with partial response
        raise RucioAuthenticationException(response, fallback_msg=str(e)) from e
