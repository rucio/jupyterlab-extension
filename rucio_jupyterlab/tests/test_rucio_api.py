# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json
from .conftest import MOCK_BASE_URL, MOCK_ACCOUNT, MOCK_AUTH_TOKEN


def test_search_did_non_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}
    mock_response_json = [
        {'scope': 'scope1', 'name': 'name1', 'type': 'container', 'bytes': None},
        {'scope': 'scope2', 'name': 'name2', 'type': 'dataset', 'bytes': None},
        {'scope': 'scope3', 'name': 'name3', 'type': 'file', 'bytes': 123}
    ]
    mock_response = '\n'.join([json.dumps(x) for x in mock_response_json])

    requests_mock.get(f"{MOCK_BASE_URL}/dids/{scope}/dids/search?type=all&long=1&name={name}", request_headers=request_headers, text=mock_response)
    response = rucio.search_did(scope, name, 'all')

    assert response == mock_response_json, "Invalid response"


def test_search_did_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}

    requests_mock.get(f"{MOCK_BASE_URL}/dids/{scope}/dids/search?type=all&long=1&name={name}", request_headers=request_headers, text='')
    response = rucio.search_did(scope, name, 'all')

    assert response == [], "Invalid response"


def test_get_files_non_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}
    mock_response_json = [
        {'scope': 'scope1', 'name': 'name1'},
        {'scope': 'scope2', 'name': 'name2'},
        {'scope': 'scope3', 'name': 'name3'}
    ]
    mock_response = '\n'.join([json.dumps(x) for x in mock_response_json])

    requests_mock.get(f"{MOCK_BASE_URL}/dids/{scope}/{name}/files", request_headers=request_headers, text=mock_response)
    response = rucio.get_files(scope, name)

    assert response == mock_response_json, "Invalid response"


def test_get_files_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}

    requests_mock.get(f"{MOCK_BASE_URL}/dids/{scope}/{name}/files", request_headers=request_headers, text='')
    response = rucio.get_files(scope, name)

    assert response == [], "Invalid response"


def test_get_rules_non_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}
    mock_response_json = [
        {'scope': 'scope1', 'name': 'name1'},
        {'scope': 'scope2', 'name': 'name2'},
        {'scope': 'scope3', 'name': 'name3'}
    ]
    mock_response = '\n'.join([json.dumps(x) for x in mock_response_json])

    requests_mock.get(f"{MOCK_BASE_URL}/dids/{scope}/{name}/rules", request_headers=request_headers, text=mock_response)
    response = rucio.get_rules(scope, name)

    assert response == mock_response_json, "Invalid response"


def test_get_rules_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}

    requests_mock.get(f"{MOCK_BASE_URL}/dids/{scope}/{name}/rules", request_headers=request_headers, text='')
    response = rucio.get_rules(scope, name)

    assert response == [], "Invalid response"


def test_get_rule_details_ok(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))
    rule_id = 'rule_id'

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}

    response_json = {'rule_id': rule_id, 'status': 'AVAILABLE'}
    requests_mock.get(f"{MOCK_BASE_URL}/rules/{rule_id}", request_headers=request_headers, json=response_json)
    response = rucio.get_rule_details(rule_id)

    assert response == response_json, "Invalid response"


def test_get_replicas_non_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}
    mock_response_json = [
        {'scope': 'scope1', 'name': 'name1'},
        {'scope': 'scope2', 'name': 'name2'},
        {'scope': 'scope3', 'name': 'name3'}
    ]
    mock_response = '\n'.join([json.dumps(x) for x in mock_response_json])

    requests_mock.get(f"{MOCK_BASE_URL}/replicas/{scope}/{name}", request_headers=request_headers, text=mock_response)
    response = rucio.get_replicas(scope, name)

    assert response == mock_response_json, "Invalid response"


def test_get_replicas_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}

    requests_mock.get(f"{MOCK_BASE_URL}/replicas/{scope}/{name}", request_headers=request_headers, text='')
    response = rucio.get_replicas(scope, name)

    assert response == [], "Invalid response"


def test_add_replication_rule(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(MOCK_AUTH_TOKEN, 1368440583))

    request_headers = {'X-Rucio-Auth-Token': MOCK_AUTH_TOKEN}
    response_json = {}
    adapter = requests_mock.post(f"{MOCK_BASE_URL}/rules/", request_headers=request_headers, json=response_json)

    mock_dids = [
        {'scope': 'scope1', 'name': 'name1'},
        {'scope': 'scope2', 'name': 'name2'},
        {'scope': 'scope3', 'name': 'name3'}
    ]
    mock_copies = 1
    mock_rse_expression = 'SWAN-EOS'
    mock_weight = 2
    mock_lifetime = 365
    mock_grouping = 'DATASET'
    mock_locked = False
    mock_source_replica_expression = 'XRD1'
    mock_activity = None
    mock_notify = 'N'
    mock_purge_replicas = False
    mock_ignore_availability = False
    mock_comment = 'Rucio'
    mock_ask_approval = False
    mock_asynchronous = False
    mock_priority = 3
    mock_meta = {}

    response = rucio.add_replication_rule(mock_dids, mock_copies, mock_rse_expression, weight=mock_weight, lifetime=mock_lifetime, grouping=mock_grouping, account=MOCK_ACCOUNT,
                                          locked=mock_locked, source_replica_expression=mock_source_replica_expression, activity=mock_activity, notify=mock_notify, purge_replicas=mock_purge_replicas,
                                          ignore_availability=mock_ignore_availability, comment=mock_comment, ask_approval=mock_ask_approval, asynchronous=mock_asynchronous, priority=mock_priority,
                                          meta=mock_meta)

    assert response == response_json, "Invalid response"

    expected_request = {'dids': mock_dids, 'copies': mock_copies, 'rse_expression': mock_rse_expression,
                        'weight': mock_weight, 'lifetime': mock_lifetime, 'grouping': mock_grouping,
                        'account': MOCK_ACCOUNT, 'locked': mock_locked, 'source_replica_expression': mock_source_replica_expression,
                        'activity': mock_activity, 'notify': mock_notify, 'purge_replicas': mock_purge_replicas,
                        'ignore_availability': mock_ignore_availability, 'comment': mock_comment, 'ask_approval': mock_ask_approval,
                        'asynchronous': mock_asynchronous, 'priority': mock_priority, 'meta': mock_meta}

    assert adapter.last_request.json() == expected_request, "Invalid request payload"
