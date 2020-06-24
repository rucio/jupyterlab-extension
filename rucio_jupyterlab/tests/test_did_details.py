"""
Possible states:
- Attachments cache: empty, exists
- File replica cache: empty, some exists, all exists
- DID states: All available, not all available
- Force fetch: no, yes

Case 1: Attachments exist, all replica cache exists, all available, no force fetch -> should not fetch
Case 2: Attachments exist, all replica cache exists, not all available, no force fetch -> should fetch rule status only
Case 3: Attachments exist, some replica cache exists, all available, no force fetch -> should fetch replicas only
Case 4: Attachments exist, some replica cache exists, not all available, no force fetch -> should fetch replicas and rule status
Case 5: Attachments exist, no replica cache exists, all available, no force fetch -> should fetch replicas only
Case 6: Attachments exist, no replica cache exists, not all available, no force fetch -> should fetch replicas and rule status
Case 7: Attachments not exist, no replica cache exists, all available, no force fetch -> should fetch replicas only
Case 8: Attachments not exist, no replica cache exists, not all available, no force fetch -> should fetch replicas and rule status
Case 9: Force fetch, all available -> should fetch replicas only
Case 10: Force fetch, not all available -> should fetch replicas and rule status
"""

import json
from unittest.mock import call
from rucio_jupyterlab.entity import AttachedFile
from rucio_jupyterlab.handlers.did_details import DIDDetailsHandler, DIDDetailsHandlerImpl
from rucio_jupyterlab.rucio import RucioAPIFactory
from .mocks.mock_db import MockDatabaseInstance, Struct
from .mocks.mock_handler import MockHandler


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


def create_mock_db_get_file_replica(exist=[], missing=[]):
    mock_replica_i = 0

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


def mock_db_set_file_replica(namespace, file_did, pfn, size):  #pylint: disable=unused-argument
    pass


def mock_db_set_attached_files(namespace, did, attached_dids):  #pylint: disable=unused-argument
    pass


def setup_common_mocks(mocker):
    mock_db = MockDatabaseInstance()
    mocker.patch("rucio_jupyterlab.handlers.did_details.get_db", return_value=mock_db)
    mocker.patch.object(mock_db, "set_attached_files", side_effect=mock_db_set_attached_files)
    mocker.patch.object(mock_db, "set_file_replica", side_effect=mock_db_set_file_replica)

    return mock_db


def test_get_did_details__no_force_fetch__attached_files_cached__all_replicas_cached__all_dids_available___should_not_fetch(rucio, mocker):
    mock_db = setup_common_mocks(mocker)
    mocker.patch.object(mock_db, "get_attached_files", return_value=MOCK_ATTACHED_FILES)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica())

    mock_scope = 'scope'
    mock_name = 'name'

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
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

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, True)

    rucio.get_replicas.assert_called_once()
    rucio.get_rules.assert_called_once()

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name2', 'path': None, 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name3', 'path': None, 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_handler(mocker, rucio):
    mock_self = MockHandler()
    mock_active_instance = 'atlas'

    def mock_get_query_argument(key, default=None):
        args = {
            'namespace': mock_active_instance,
            'poll': '0',
            'did': 'scope:name'
        }
        return args.get(key, default)

    mocker.patch.object(mock_self, 'get_query_argument', side_effect=mock_get_query_argument)

    rucio_api_factory = RucioAPIFactory(None)
    mocker.patch.object(rucio_api_factory, 'for_instance', return_value=rucio)
    mock_self.rucio = rucio_api_factory

    mock_did_details = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 456}
    ]

    class MockDIDDetailsHandlerImpl(DIDDetailsHandlerImpl):
        def get_did_details(self, scope, name, force_fetch=False):
            return mock_did_details

    mocker.patch('rucio_jupyterlab.handlers.did_details.DIDDetailsHandlerImpl', MockDIDDetailsHandlerImpl)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        assert finish_json == mock_did_details, "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    DIDDetailsHandler.get(mock_self)

    calls = [call('namespace'), call('poll', '0'), call('did')]
    mock_self.get_query_argument.assert_has_calls(calls, any_order=True)  # pylint: disable=no-member
    rucio_api_factory.for_instance.assert_called_once_with(mock_active_instance)  # pylint: disable=no-member
