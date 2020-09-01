# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json
from unittest.mock import call
from rucio_jupyterlab.handlers.did_browser import DIDBrowserHandler, DIDBrowserHandlerImpl
from rucio_jupyterlab.entity import AttachedFile
from rucio_jupyterlab.rucio import RucioAPIFactory
from .mocks.mock_db import MockDatabaseInstance
from .mocks.mock_handler import MockHandler


MOCK_ACTIVE_INSTANCE = 'atlas'


def test_get_files__cache_exist__no_force_fetch(mocker, rucio):
    """
    If cache exist and force_fetch is false, assert method
    to call db.get_attached_files and NOT rucio.get_replicas.
    Assert their call parameters as well.
    """

    mock_db = MockDatabaseInstance()
    mocker.patch('rucio_jupyterlab.handlers.did_browser.get_db', return_value=mock_db)
    mocker.patch.object(rucio, 'get_replicas', return_value=[])

    mock_attached_files = [
        AttachedFile('scope1:name1', 123456),
        AttachedFile('scope2:name2', 789456),
        AttachedFile('scope3:name3', 1)
    ]

    mocker.patch.object(mock_db, 'get_attached_files', return_value=mock_attached_files)

    handler = DIDBrowserHandlerImpl(MOCK_ACTIVE_INSTANCE, rucio)
    result = handler.get_files('scope', 'name', False)

    rucio.get_replicas.assert_not_called()
    mock_db.get_attached_files.assert_called_once_with(namespace=MOCK_ACTIVE_INSTANCE, did='scope:name')     # pylint: disable=no-member

    expected = [x.__dict__ for x in mock_attached_files]
    assert result == expected, "Invalid return value"


def test_get_files__cache_exist__force_fetch(mocker, rucio):
    """
    If cache exist and force_fetch is true, assert method
    to NOT call db.get_attached_files and call rucio.get_replicas.
    Assert their call parameters as well.
    """

    mock_db = MockDatabaseInstance()
    mocker.patch('rucio_jupyterlab.handlers.did_browser.get_db', return_value=mock_db)

    mock_replicas = [
        {'scope': 'scope1', 'name': 'name1', 'bytes': 123456},
        {'scope': 'scope2', 'name': 'name2', 'bytes': 789456},
        {'scope': 'scope3', 'name': 'name3', 'bytes': 1}
    ]

    mock_attached_files = [
        AttachedFile(did=(d.get('scope') + ':' + d.get('name')), size=d.get('bytes'))
        for d in mock_replicas
    ]

    mocker.patch.object(rucio, 'get_replicas', return_value=mock_replicas)
    mocker.patch.object(mock_db, 'get_attached_files', return_value=mock_attached_files)

    handler = DIDBrowserHandlerImpl(MOCK_ACTIVE_INSTANCE, rucio)
    result = handler.get_files('scope', 'name', True)

    rucio.get_replicas.assert_called_once_with('scope', 'name')
    mock_db.get_attached_files.assert_not_called()   # pylint: disable=no-member

    expected = [x.__dict__ for x in mock_attached_files]
    assert result == expected, "Invalid return value"


def test_get_files__cache_not_exist(mocker, rucio):
    """
    If cache not exist and force_fetch is false, assert method
    to call db.get_attached_files and rucio.get_replicas.
    Assert their call parameters as well.
    """

    mock_db = MockDatabaseInstance()
    mocker.patch('rucio_jupyterlab.handlers.did_browser.get_db', return_value=mock_db)

    mock_replicas = [
        {'scope': 'scope1', 'name': 'name1', 'bytes': 123456},
        {'scope': 'scope2', 'name': 'name2', 'bytes': 789456},
        {'scope': 'scope3', 'name': 'name3', 'bytes': 1}
    ]

    mock_attached_files = [
        AttachedFile(did=(d.get('scope') + ':' + d.get('name')), size=d.get('bytes'))
        for d in mock_replicas
    ]

    mocker.patch.object(rucio, 'get_replicas', return_value=mock_replicas)
    mocker.patch.object(mock_db, 'get_attached_files', return_value=None)

    handler = DIDBrowserHandlerImpl(MOCK_ACTIVE_INSTANCE, rucio)
    result = handler.get_files('scope', 'name')

    rucio.get_replicas.assert_called_once_with('scope', 'name')  # pylint: disable=no-member
    mock_db.get_attached_files.assert_called_once_with(namespace=MOCK_ACTIVE_INSTANCE, did='scope:name')  # pylint: disable=no-member

    expected = [x.__dict__ for x in mock_attached_files]
    assert result == expected, "Invalid return value"


def test_get_handler(mocker, rucio):
    mock_self = MockHandler()

    def mock_get_query_argument(key, default=None):
        args = {
            'namespace': MOCK_ACTIVE_INSTANCE,
            'poll': '0',
            'did': 'scope:name'
        }
        return args.get(key, default)

    mocker.patch.object(mock_self, 'get_query_argument', side_effect=mock_get_query_argument)

    rucio_api_factory = RucioAPIFactory(None)
    mocker.patch.object(rucio_api_factory, 'for_instance', return_value=rucio)
    mock_self.rucio = rucio_api_factory

    mock_attached_files = [
        AttachedFile('scope1:name1', 123456),
        AttachedFile('scope2:name2', 789456),
        AttachedFile('scope3:name3', 1)
    ]

    class MockDIDBrowserHandlerImpl(DIDBrowserHandlerImpl):
        def get_files(self, scope, name, force_fetch=False):
            return [x.__dict__ for x in mock_attached_files]

    mocker.patch('rucio_jupyterlab.handlers.did_browser.DIDBrowserHandlerImpl', MockDIDBrowserHandlerImpl)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        assert finish_json == [x.__dict__ for x in mock_attached_files], "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    DIDBrowserHandler.get(mock_self)

    calls = [call('namespace'), call('poll', '0'), call('did')]
    mock_self.get_query_argument.assert_has_calls(calls, any_order=True)  # pylint: disable=no-member

    rucio_api_factory.for_instance.assert_called_once_with(MOCK_ACTIVE_INSTANCE)  # pylint: disable=no-member
