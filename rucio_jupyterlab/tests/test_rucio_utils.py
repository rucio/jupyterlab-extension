# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021

from unittest.mock import patch, mock_open
from rucio_jupyterlab.rucio.utils import parse_timestamp, get_oidc_token


def test_parse_timestamp_returns_correct_timezone_utc():
    time_str = 'Mon, 13 May 2013 10:23:03 UTC'
    expected_output = 1368440583
    assert parse_timestamp(time_str) == expected_output, "Invalid timestamp conversion"


def test_get_oidc_token__oidc_env__env_exists__should_return_env_value(mocker):
    mocker.patch.dict('os.environ', {'ACCESS_TOKEN': 'access_token'})
    assert get_oidc_token(oidc_auth='env', oidc_auth_source='ACCESS_TOKEN') == 'access_token', "Invalid token value"


def test_get_oidc_token__oidc_env__env_not_exists__should_return_none(mocker):
    mocker.patch.dict('os.environ', {})
    assert get_oidc_token(oidc_auth='env', oidc_auth_source='ACCESS_TOKEN') == None, "Invalid token value"


def test_get_oidc_token__oidc_file__file_exists__should_return_file_value(mocker):
    with patch("builtins.open", mock_open(read_data="access_token")) as mock_file:
        assert get_oidc_token(oidc_auth='file', oidc_auth_source='/tmp/oauth2') == 'access_token'
        mock_file.assert_called_with('/tmp/oauth2')


def test_get_oidc_token__oidc_file__file_not_exists__should_return_none(mocker):
    # Since we cannot mock a nonexisting file, we just enter a filename that should not exist in the test runner.
    assert get_oidc_token(oidc_auth='file', oidc_auth_source='/tmp/oauth2-should-not-exists') == None
