# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from rucio_jupyterlab.entity import AttachedFile
from rucio_jupyterlab.mode_handlers.replica import ReplicaModeHandler
from .mocks.mock_db import MockDatabaseInstance, Struct


MOCK_ATTACHED_FILES = [
    AttachedFile(did='scope:name1', size=123),
    AttachedFile(did='scope:name2', size=456),
    AttachedFile(did='scope:name3', size=789)
]

mock_rucio_replicas_all_available = [
    {
        "adler32": "01a100a2",
        "name": "name1",
        "rses": {
            "SWAN-EOS": [
                "root://xrd1:1094//eos/docker/user/rucio/scope:name1"
            ]
        },
        "bytes": 123,
        "states": {
            "SWAN-EOS": "AVAILABLE",
            "XRD1": "AVAILABLE"
        },
        "scope": "scope"
    },
    {
        "adler32": "01a100a2",
        "name": "name2",
        "rses": {
            "SWAN-EOS": [
                "root://xrd1:1094//eos/docker/user/rucio/scope:name2"
            ]
        },
        "bytes": 123,
        "states": {
            "SWAN-EOS": "AVAILABLE",
            "XRD1": "AVAILABLE"
        },
        "scope": "scope"
    },
    {
        "adler32": "01a100a2",
        "name": "name3",
        "rses": {
            "SWAN-EOS": [
                "root://xrd1:1094//eos/docker/user/rucio/scope:name3"
            ]
        },
        "bytes": 123,
        "states": {
            "SWAN-EOS": "AVAILABLE",
            "XRD1": "AVAILABLE"
        },
        "scope": "scope"
    }
]

mock_rucio_replicas_some_available = [
    {
        "adler32": "01a100a2",
        "name": "name1",
        "rses": {
            "SWAN-EOS": [
                "root://xrd1:1094//eos/docker/user/rucio/scope:name1"
            ]
        },
        "bytes": 123,
        "states": {
            "SWAN-EOS": "AVAILABLE",
        },
        "scope": "scope"
    },
    {
        "adler32": "01a100a2",
        "name": "name2",
        "rses": {
        },
        "bytes": 123,
        "states": {
        },
        "scope": "scope"
    },
    {
        "adler32": "01a100a2",
        "name": "name3",
        "rses": {
        },
        "bytes": 123,
        "states": {
        },
        "scope": "scope"
    }
]

mock_rucio_rule_status_ok = [
    {'scope': 'scope', 'name': 'name', 'state': 'OK', 'rse_expression': 'SWAN-EOS'}
]

mock_rucio_rule_status_replicating = [
    {'scope': 'scope', 'name': 'name', 'state': 'REPLICATING', 'rse_expression': 'SWAN-EOS'}
]


def create_mock_db_get_file_replica(exist=None, missing=None):
    mock_replica_i = 0

    if not exist:
        exist = []

    if not missing:
        missing = []

    def mock_db_get_file_replica(namespace, did):
        nonlocal mock_replica_i
        if mock_replica_i < len(missing) and missing[mock_replica_i]:
            mock_replica_i += 1
            return None

        if mock_replica_i >= len(exist):
            should_exist = True
        else:
            should_exist = exist[mock_replica_i]
            mock_replica_i += 1

        pfn = "root://xrd1:1094//test/" + did if should_exist else None

        return Struct(namespace=namespace, did=did, pfn=pfn, size=123, expiry=123456798)

    return mock_db_get_file_replica


def mock_db_set_file_replica(namespace, file_did, pfn, size):  # pylint: disable=unused-argument
    pass


def mock_db_set_attached_files(namespace, did, attached_dids):  # pylint: disable=unused-argument
    pass


def setup_common_mocks(mocker):
    mock_db = MockDatabaseInstance()
    mocker.patch("rucio_jupyterlab.mode_handlers.replica.get_db", return_value=mock_db)
    mocker.patch.object(mock_db, "set_attached_files", side_effect=mock_db_set_attached_files)
    mocker.patch.object(mock_db, "set_file_replica", side_effect=mock_db_set_file_replica)

    return mock_db


def test_get_did_details__no_force_fetch__attached_files_cached__all_replicas_cached__all_dids_available___should_not_fetch(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica())

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 123},
        {'status': 'OK', 'did': 'scope:name3', 'path': '/eos/user/rucio/scope:name3', 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__all_replicas_cached__not_all_dids_available___should_fetch_rule__status_replicating(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(exist=[False, True, True]))
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_replicating)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    rucio.get_rules.assert_called_once()

    expected_result = [
        {'status': 'REPLICATING', 'did': 'scope:name1', 'path': None, 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 123},
        {'status': 'OK', 'did': 'scope:name3', 'path': '/eos/user/rucio/scope:name3', 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__all_replicas_cached__not_all_dids_available___should_fetch_rule__status_not_available(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(exist=[False, True, True]))
    mocker.patch.object(rucio, 'get_rules', return_value=[])

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    rucio.get_rules.assert_called_once()

    expected_result = [
        {'status': 'NOT_AVAILABLE', 'did': 'scope:name1', 'path': None, 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 123},
        {'status': 'OK', 'did': 'scope:name3', 'path': '/eos/user/rucio/scope:name3', 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__all_replicas_cached__not_all_dids_available___should_fetch_rule__status_ok(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(exist=[False, True, True]))
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_ok)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    rucio.get_rules.assert_called_once()

    expected_result = [
        {'status': 'REPLICATING', 'did': 'scope:name1', 'path': None, 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 123},
        {'status': 'OK', 'did': 'scope:name3', 'path': '/eos/user/rucio/scope:name3', 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__some_replicas_cached__all_dids_available___should_fetch_replica(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(exist=[True, True, True], missing=[True, False, False]))
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_ok)
    mocker.patch.object(rucio, "get_replicas", return_value=mock_rucio_replicas_all_available)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    rucio.get_replicas.assert_called_once()
    rucio.get_rules.assert_not_called()

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 123},
        {'status': 'OK', 'did': 'scope:name3', 'path': '/eos/user/rucio/scope:name3', 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__some_replicas_cached__not_all_dids_available___should_fetch_replica_and_rule(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(exist=[True, True, False], missing=[True, False, False]))
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_replicating)
    mocker.patch.object(rucio, "get_replicas", return_value=mock_rucio_replicas_some_available)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    rucio.get_replicas.assert_called_once()
    rucio.get_rules.assert_called_once()

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name2', 'path': None, 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name3', 'path': None, 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__no_replicas_cached__all_dids_available___should_fetch_replica(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", return_value=None)
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_ok)
    mocker.patch.object(rucio, "get_replicas", return_value=mock_rucio_replicas_all_available)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    rucio.get_replicas.assert_called_once()
    rucio.get_rules.assert_not_called()

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 123},
        {'status': 'OK', 'did': 'scope:name3', 'path': '/eos/user/rucio/scope:name3', 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__no_replicas_cached__not_all_dids_available___should_fetch_replica_and_rule(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", return_value=None)
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_replicating)
    mocker.patch.object(rucio, "get_replicas", return_value=mock_rucio_replicas_some_available)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    rucio.get_replicas.assert_called_once()
    rucio.get_rules.assert_called_once()

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name2', 'path': None, 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name3', 'path': None, 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_not_cached__no_replicas_cached__all_dids_available___should_fetch_replica(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=None)
    mocker.patch.object(mock_db, "get_file_replica", return_value=None)
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_ok)
    mocker.patch.object(rucio, "get_replicas", return_value=mock_rucio_replicas_all_available)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    rucio.get_replicas.assert_called_once()
    rucio.get_rules.assert_not_called()

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 123},
        {'status': 'OK', 'did': 'scope:name3', 'path': '/eos/user/rucio/scope:name3', 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_not_cached__no_replicas_cached__not_all_dids_available___should_fetch_replica_and_rule(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=None)
    mocker.patch.object(mock_db, "get_file_replica", return_value=None)
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_replicating)
    mocker.patch.object(rucio, "get_replicas", return_value=mock_rucio_replicas_some_available)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    rucio.get_replicas.assert_called_once()
    rucio.get_rules.assert_called_once()

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name2', 'path': None, 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name3', 'path': None, 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__force_fetch__all_dids_available___should_fetch_replica(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(exist=[True, True, False]))
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_replicating)
    mocker.patch.object(rucio, "get_replicas", return_value=mock_rucio_replicas_all_available)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, True)

    rucio.get_replicas.assert_called_once()
    rucio.get_rules.assert_not_called()

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 123},
        {'status': 'OK', 'did': 'scope:name3', 'path': '/eos/user/rucio/scope:name3', 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__force_fetch__not_all_dids_available___should_fetch_replica_and_rule(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(exist=[True, True, False]))
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_replicating)
    mocker.patch.object(rucio, "get_replicas", return_value=mock_rucio_replicas_some_available)

    mock_scope = 'scope'
    mock_name = 'name'

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, True)

    rucio.get_replicas.assert_called_once()
    rucio.get_rules.assert_called_once()

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name2', 'path': None, 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name3', 'path': None, 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_make_available__lifetime_specified__should_call_add_rule(mocker, rucio):
    mocker.patch.dict(rucio.instance_config, {'destination_rse': 'SWAN-EOS', 'replication_rule_lifetime_days': 1})
    mocker.patch.object(rucio, 'add_replication_rule', return_value={})

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    handler.make_available(scope='scope', name='name')

    expected_dids = [{'scope': 'scope', 'name': 'name'}]
    rucio.add_replication_rule.assert_called_once_with(dids=expected_dids, rse_expression='SWAN-EOS', copies=1, lifetime=86400)


def test_make_available__lifetime_not_specified__should_call_add_rule__lifetime_none(mocker, rucio):
    mocker.patch.dict(rucio.instance_config, {'destination_rse': 'SWAN-EOS'})
    mocker.patch.object(rucio, 'add_replication_rule', return_value={})

    handler = ReplicaModeHandler(namespace='atlas', rucio=rucio)
    handler.make_available(scope='scope', name='name')

    expected_dids = [{'scope': 'scope', 'name': 'name'}]
    rucio.add_replication_rule.assert_called_once_with(dids=expected_dids, rse_expression='SWAN-EOS', copies=1, lifetime=None)
