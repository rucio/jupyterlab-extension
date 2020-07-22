import json
from unittest.mock import call
from rucio_jupyterlab.handlers.did_search import DIDSearchHandler, DIDSearchHandlerImpl
from rucio_jupyterlab.entity import AttachedFile
from rucio_jupyterlab.rucio import RucioAPIFactory
from .mocks.mock_db import MockDatabaseInstance
from .mocks.mock_handler import MockHandler


MOCK_ACTIVE_INSTANCE = 'atlas'


def test_search_did__with_wildcard__wildcard_enabled__correct_response(mocker, rucio):
    """
    If cache exist and force_fetch is false, assert method
    to call db.get_attached_files and NOT rucio.get_replicas.
    Assert their call parameters as well.
    """

    mocker.patch.object(rucio, 'search_did', return_value=[
        {'scope': 'scope', 'name': 'name1', 'bytes': None, 'did_type': 'CONTAINER'},
        {'scope': 'scope', 'name': 'name2', 'bytes': None, 'did_type': 'DATASET'},
        {'scope': 'scope', 'name': 'name3', 'bytes': 123, 'did_type': 'FILE'}
    ])

    handler = DIDSearchHandlerImpl(MOCK_ACTIVE_INSTANCE, rucio)
    result = handler.search_did('scope', 'name*', 'all')

    rucio.search_did.assert_called_once_with('scope', 'name*', 'all')

    expected = [
        {'did': 'scope:name1', 'size': None, 'type': 'container'},
        {'did': 'scope:name2', 'size': None, 'type': 'dataset'},
        {'did': 'scope:name3', 'size': 123, 'type': 'file'}
    ]

    assert result == expected, "Invalid return value"
