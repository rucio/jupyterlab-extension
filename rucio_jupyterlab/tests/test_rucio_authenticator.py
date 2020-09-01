# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from rucio_jupyterlab.rucio.authenticators import authenticate_userpass, authenticate_x509


def test_authenticate_userpass_call_requests(requests_mock):
    mock_base_url = "https://rucio/"
    mock_username = "username"
    mock_password = "password"
    mock_account = "account"
    mock_app_id = "app_id"
    mock_vo = "def"
    mock_auth_token = 'abcde_token_ghijk'

    request_headers = {
        'X-Rucio-Account': mock_account, 'X-Rucio-Username': mock_username,
        'X-Rucio-Password': mock_password, 'X-Rucio-AppID': mock_app_id,
        'X-Rucio-VO': mock_vo
    }

    response_headers = {
        'X-Rucio-Auth-Token': mock_auth_token,
        'X-Rucio-Auth-Token-Expires': 'Mon, 13 May 2013 10:23:03 UTC'
    }

    requests_mock.get(f'{mock_base_url}/auth/userpass', request_headers=request_headers, headers=response_headers)

    expected_output = (mock_auth_token, 1368440583)
    response = authenticate_userpass(mock_base_url, mock_username, mock_password, account=mock_account, vo=mock_vo, app_id=mock_app_id)
    assert response == expected_output, "Invalid return value"


def test_authenticate_x509_call_requests(requests_mock):
    mock_base_url = "https://rucio/"
    mock_account = "account"
    mock_app_id = "app_id"
    mock_vo = "def"
    mock_auth_token = 'abcde_token_ghijk'

    mock_cert_path = '/eos/user/certs/cert.pem'
    mock_key_path = '/eos/user/certs/key.pem'

    request_headers = {
        'X-Rucio-Account': mock_account, 'X-Rucio-AppID': mock_app_id, 'X-Rucio-VO': mock_vo
    }

    response_headers = {
        'X-Rucio-Auth-Token': mock_auth_token,
        'X-Rucio-Auth-Token-Expires': 'Mon, 13 May 2013 10:23:03 UTC'
    }

    requests_mock.get(f'{mock_base_url}/auth/x509', request_headers=request_headers, headers=response_headers)

    expected_output = (mock_auth_token, 1368440583)
    response = authenticate_x509(mock_base_url, cert_path=mock_cert_path, key_path=mock_key_path, account=mock_account, vo=mock_vo, app_id=mock_app_id)
    assert response == expected_output, "Invalid return value"
    assert requests_mock.last_request.cert == (mock_cert_path, mock_key_path), "Invalid certs"
