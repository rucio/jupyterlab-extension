import pytest
import json
from rucio_jupyterlab.rucio import RucioAPI
from .conftest import mock_base_url, mock_username, mock_password, mock_account, mock_app_id, mock_auth_token
import rucio_jupyterlab

def test_get_files_non_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(mock_auth_token, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': mock_auth_token}
    mock_response_json = [
        {'scope': 'scope1', 'name': 'name1'},
        {'scope': 'scope2', 'name': 'name2'},
        {'scope': 'scope3', 'name': 'name3'}
    ]
    mock_response = '\n'.join([json.dumps(x) for x in mock_response_json])

    requests_mock.get(f"{mock_base_url}/dids/{scope}/{name}/files", request_headers=request_headers, text=mock_response)
    response = rucio.get_files(scope, name)

    assert response == mock_response_json, "Invalid response"


def test_get_files_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(mock_auth_token, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': mock_auth_token}

    requests_mock.get(f"{mock_base_url}/dids/{scope}/{name}/files", request_headers=request_headers, text='')
    response = rucio.get_files(scope, name)

    assert response == [], "Invalid response"


def test_get_rules_non_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(mock_auth_token, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': mock_auth_token}
    mock_response_json = [
        {'scope': 'scope1', 'name': 'name1'},
        {'scope': 'scope2', 'name': 'name2'},
        {'scope': 'scope3', 'name': 'name3'}
    ]
    mock_response = '\n'.join([json.dumps(x) for x in mock_response_json])

    requests_mock.get(f"{mock_base_url}/dids/{scope}/{name}/rules", request_headers=request_headers, text=mock_response)
    response = rucio.get_rules(scope, name)

    assert response == mock_response_json, "Invalid response"


def test_get_rules_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(mock_auth_token, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': mock_auth_token}

    requests_mock.get(f"{mock_base_url}/dids/{scope}/{name}/rules", request_headers=request_headers, text='')
    response = rucio.get_rules(scope, name)

    assert response == [], "Invalid response"


def test_get_rule_details_ok(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(mock_auth_token, 1368440583))
    rule_id = 'rule_id'

    request_headers = {'X-Rucio-Auth-Token': mock_auth_token}

    response_json = {'rule_id': rule_id, 'status': 'AVAILABLE'}
    requests_mock.get(f"{mock_base_url}/rules/{rule_id}", request_headers=request_headers, json=response_json)
    response = rucio.get_rule_details(rule_id)

    assert response == response_json, "Invalid response"


def test_get_replicas_non_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(mock_auth_token, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': mock_auth_token}
    mock_response_json = [
        {'scope': 'scope1', 'name': 'name1'},
        {'scope': 'scope2', 'name': 'name2'},
        {'scope': 'scope3', 'name': 'name3'}
    ]
    mock_response = '\n'.join([json.dumps(x) for x in mock_response_json])

    requests_mock.get(f"{mock_base_url}/replicas/{scope}/{name}", request_headers=request_headers, text=mock_response)
    response = rucio.get_replicas(scope, name)

    assert response == mock_response_json, "Invalid response"


def test_get_replicas_empty_result(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(mock_auth_token, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': mock_auth_token}

    requests_mock.get(f"{mock_base_url}/replicas/{scope}/{name}", request_headers=request_headers, text='')
    response = rucio.get_replicas(scope, name)

    assert response == [], "Invalid response"


def test_add_replication_rule(rucio, mocker, requests_mock):
    mocker.patch('rucio_jupyterlab.rucio.authenticate_userpass', return_value=(mock_auth_token, 1368440583))
    scope, name = "scope", "name"

    request_headers = {'X-Rucio-Auth-Token': mock_auth_token}
    response_json = {}
    adapter = requests_mock.post(f"{mock_base_url}/rules/", request_headers=request_headers, json=response_json)

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

    response = rucio.add_replication_rule(mock_dids, mock_copies, mock_rse_expression, weight=mock_weight, lifetime=mock_lifetime, grouping=mock_grouping, account=mock_account,
                                          locked=mock_locked, source_replica_expression=mock_source_replica_expression, activity=mock_activity, notify=mock_notify, purge_replicas=mock_purge_replicas,
                                          ignore_availability=mock_ignore_availability, comment=mock_comment, ask_approval=mock_ask_approval, asynchronous=mock_asynchronous, priority=mock_priority,
                                          meta=mock_meta)

    assert response == response_json, "Invalid response"

    expected_request = {'dids': mock_dids, 'copies': mock_copies, 'rse_expression': mock_rse_expression,
                        'weight': mock_weight, 'lifetime': mock_lifetime, 'grouping': mock_grouping,
                        'account': mock_account, 'locked': mock_locked, 'source_replica_expression': mock_source_replica_expression,
                        'activity': mock_activity, 'notify': mock_notify, 'purge_replicas': mock_purge_replicas,
                        'ignore_availability': mock_ignore_availability, 'comment': mock_comment, 'ask_approval': mock_ask_approval,
                        'asynchronous': mock_asynchronous, 'priority': mock_priority, 'meta': mock_meta}

    assert adapter.last_request.json() == expected_request, "Invalid request payload"
