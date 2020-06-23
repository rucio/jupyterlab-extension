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

"""

from .mocks.mock_db import MockDatabaseInstance, Struct
from rucio_jupyterlab.entity import AttachedFile, PfnFileReplica
from rucio_jupyterlab.handlers.did_details import DIDDetailsHandlerImpl

mock_attached_files = [
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
        "name": "name1",
        "rses": {
                "SWAN-EOS": [
                    "root://xrd1:1094//eos/docker/user/rucio/test/scope:name2"
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
                    "root://xrd1:1094//eos/docker/user/rucio/test/scope:name3"
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
                    "root://xrd1:1094//eos/docker/user/rucio/test/scope:name1"
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
        "name": "name1",
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


def create_mock_db_get_file_replica(all_exists=True):
    global mock_replica_should_exist
    mock_replica_should_exist = True

    def mock_db_get_file_replica(namespace, did):
        global mock_replica_should_exist
        pfn = "root://xrd1:1094//test/" + did if mock_replica_should_exist else None
        if not all_exists:
            mock_replica_should_exist = False
        return Struct(namespace=namespace, did=did, pfn=pfn, size=123, expiry=123456798)

    return mock_db_get_file_replica


def mock_db_set_file_replica(namespace, file_did, pfn, size):
    pass


def mock_db_set_attached_files(namespace, did, attached_dids):
    pass


def test_get_did_details__no_force_fetch__attached_files_cached__all_replicas_cached__all_dids_available___should_not_fetch(rucio, mocker):
    mock_db = MockDatabaseInstance()
    mocker.patch("rucio_jupyterlab.handlers.did_details.get_db", return_value=mock_db)
    mocker.patch.object(mock_db, "get_attached_files", return_value=mock_attached_files)
    mocker.patch.object(mock_db, "set_attached_files", side_effect=mock_db_set_attached_files)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(all_exists=True))
    mocker.patch.object(mock_db, "set_file_replica", side_effect=mock_db_set_file_replica)

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
    mock_db = MockDatabaseInstance()
    mocker.patch("rucio_jupyterlab.handlers.did_details.get_db", return_value=mock_db)
    mocker.patch.object(mock_db, "get_attached_files", return_value=mock_attached_files)
    mocker.patch.object(mock_db, "set_attached_files", side_effect=mock_db_set_attached_files)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(all_exists=False))
    mocker.patch.object(mock_db, "set_file_replica", side_effect=mock_db_set_file_replica)
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_replicating)
    mock_scope = 'scope'
    mock_name = 'name'

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name2', 'path': None, 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name3', 'path': None, 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__all_replicas_cached__not_all_dids_available___should_fetch_rule__status_not_available(rucio, mocker):
    mock_db = MockDatabaseInstance()
    mocker.patch("rucio_jupyterlab.handlers.did_details.get_db", return_value=mock_db)
    mocker.patch.object(mock_db, "get_attached_files", return_value=mock_attached_files)
    mocker.patch.object(mock_db, "set_attached_files", side_effect=mock_db_set_attached_files)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(all_exists=False))
    mocker.patch.object(mock_db, "set_file_replica", side_effect=mock_db_set_file_replica)
    mocker.patch.object(rucio, 'get_rules', return_value=[])
    mock_scope = 'scope'
    mock_name = 'name'

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'NOT_AVAILABLE', 'did': 'scope:name2', 'path': None, 'size': 123},
        {'status': 'NOT_AVAILABLE', 'did': 'scope:name3', 'path': None, 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__all_replicas_cached__not_all_dids_available___should_fetch_rule__status_ok(rucio, mocker):
    mock_db = MockDatabaseInstance()
    mocker.patch("rucio_jupyterlab.handlers.did_details.get_db", return_value=mock_db)
    mocker.patch.object(mock_db, "get_attached_files", return_value=mock_attached_files)
    mocker.patch.object(mock_db, "set_attached_files", side_effect=mock_db_set_attached_files)
    mocker.patch.object(mock_db, "get_file_replica", side_effect=create_mock_db_get_file_replica(all_exists=False))
    mocker.patch.object(mock_db, "set_file_replica", side_effect=mock_db_set_file_replica)
    mocker.patch.object(rucio, 'get_rules', return_value=mock_rucio_rule_status_ok)
    mock_scope = 'scope'
    mock_name = 'name'

    handler = DIDDetailsHandlerImpl(namespace='atlas', rucio=rucio)
    result = handler.get_did_details(mock_scope, mock_name, False)

    expected_result = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name2', 'path': None, 'size': 123},
        {'status': 'REPLICATING', 'did': 'scope:name3', 'path': None, 'size': 123}
    ]

    assert result == expected_result, "Invalid return value"


def test_get_did_details__no_force_fetch__attached_files_cached__some_replicas_cached__all_dids_available___should_fetch_replica(rucio, mocker):
    mocker.patch.object(rucio, "get_replicas", return_value=mock_rucio_replicas_all_available)


def test_get_did_details__no_force_fetch__attached_files_cached__some_replicas_cached__not_all_dids_available___should_fetch_replica_and_rule(rucio, mocker):
    pass


def test_get_did_details__no_force_fetch__attached_files_cached__no_replicas_cached__all_dids_available___should_fetch_replica(rucio, mocker):
    pass


def test_get_did_details__no_force_fetch__attached_files_cached__no_replicas_cached__not_all_dids_available___should_fetch_replica_and_rule(rucio, mocker):
    pass


def test_get_did_details__no_force_fetch__attached_files_not_cached__no_replicas_cached__all_dids_available___should_fetch_replica(rucio, mocker):
    pass


def test_get_did_details__no_force_fetch__attached_files_not_cached__no_replicas_cached__not_all_dids_available___should_fetch_replica_and_rule(rucio, mocker):
    pass
