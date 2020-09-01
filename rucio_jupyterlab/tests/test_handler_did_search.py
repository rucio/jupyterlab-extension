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
import pytest
from rucio_jupyterlab.handlers.did_search import DIDSearchHandler, DIDSearchHandlerImpl, WildcardDisallowedException
from rucio_jupyterlab.rucio import RucioAPIFactory
from .mocks.mock_handler import MockHandler


MOCK_ACTIVE_INSTANCE = 'atlas'


def test_search_did__with_wildcard__wildcard_enabled__should_return_correct_response(mocker, rucio):
    rucio.instance_config['wildcard_enabled'] = True

    mocker.patch.object(rucio, 'search_did', return_value=[
        {'scope': 'scope', 'name': 'name1', 'bytes': None, 'did_type': 'CONTAINER'},
        {'scope': 'scope', 'name': 'name2', 'bytes': None, 'did_type': 'DATASET'},
        {'scope': 'scope', 'name': 'name3', 'bytes': 123, 'did_type': 'FILE'}
    ])

    handler = DIDSearchHandlerImpl(MOCK_ACTIVE_INSTANCE, rucio)
    result = handler.search_did('scope', 'name*', 'all', 100)

    rucio.search_did.assert_called_once_with('scope', 'name*', 'all', 100)

    expected = [
        {'did': 'scope:name1', 'size': None, 'type': 'container'},
        {'did': 'scope:name2', 'size': None, 'type': 'dataset'},
        {'did': 'scope:name3', 'size': 123, 'type': 'file'}
    ]

    assert result == expected, "Invalid return value"


def test_search_did__without_wildcard__wildcard_disabled__should_return_correct_response(mocker, rucio):
    rucio.instance_config['wildcard_enabled'] = False

    mocker.patch.object(rucio, 'search_did', return_value=[
        {'scope': 'scope', 'name': 'name1', 'bytes': None, 'did_type': 'CONTAINER'},
        {'scope': 'scope', 'name': 'name2', 'bytes': None, 'did_type': 'DATASET'},
        {'scope': 'scope', 'name': 'name3', 'bytes': 123, 'did_type': 'FILE'}
    ])

    handler = DIDSearchHandlerImpl(MOCK_ACTIVE_INSTANCE, rucio)
    result = handler.search_did('scope', 'name', 'all', 100)

    rucio.search_did.assert_called_once_with('scope', 'name', 'all', 100)

    expected = [
        {'did': 'scope:name1', 'size': None, 'type': 'container'},
        {'did': 'scope:name2', 'size': None, 'type': 'dataset'},
        {'did': 'scope:name3', 'size': 123, 'type': 'file'}
    ]

    assert result == expected, "Invalid return value"


def test_search_did__with_wildcard__wildcard_disabled__should_raise_exception(mocker, rucio):
    rucio.instance_config['wildcard_enabled'] = False

    mocker.patch.object(rucio, 'search_did', return_value=[
        {'scope': 'scope', 'name': 'name1', 'bytes': None, 'did_type': 'CONTAINER'},
        {'scope': 'scope', 'name': 'name2', 'bytes': None, 'did_type': 'DATASET'},
        {'scope': 'scope', 'name': 'name3', 'bytes': 123, 'did_type': 'FILE'}
    ])

    handler = DIDSearchHandlerImpl(MOCK_ACTIVE_INSTANCE, rucio)

    with pytest.raises(WildcardDisallowedException):
        handler.search_did('scope', 'name*', 'all', 100)
        rucio.search_did.assert_called_once_with('scope', 'name', 'all', 100)


def test_search_did__with_percent_wildcard__wildcard_disabled__should_raise_exception(mocker, rucio):
    rucio.instance_config['wildcard_enabled'] = False

    mocker.patch.object(rucio, 'search_did', return_value=[
        {'scope': 'scope', 'name': 'name1', 'bytes': None, 'did_type': 'CONTAINER'},
        {'scope': 'scope', 'name': 'name2', 'bytes': None, 'did_type': 'DATASET'},
        {'scope': 'scope', 'name': 'name3', 'bytes': 123, 'did_type': 'FILE'}
    ])

    handler = DIDSearchHandlerImpl(MOCK_ACTIVE_INSTANCE, rucio)

    with pytest.raises(WildcardDisallowedException):
        handler.search_did('scope', 'name%', 'all', 100)
        rucio.search_did.assert_called_once_with('scope', 'name', 'all', 100)


def test_get_handler__inputs_correct__should_not_error(mocker, rucio):
    mock_self = MockHandler()

    def mock_get_query_argument(key, default=None):
        args = {
            'namespace': MOCK_ACTIVE_INSTANCE,
            'type': 'all',
            'did': 'scope:name'
        }
        return args.get(key, default)

    mocker.patch.object(mock_self, 'get_query_argument', side_effect=mock_get_query_argument)

    class MockDIDSearchHandler(DIDSearchHandlerImpl):
        @staticmethod
        def search_did(scope, name, search_type='all', limit=100):
            return [
                {'did': 'scope:name1', 'size': None, 'type': 'container'},
                {'did': 'scope:name2', 'size': None, 'type': 'dataset'},
                {'did': 'scope:name3', 'size': 123, 'type': 'file'}
            ]

    mocker.patch('rucio_jupyterlab.handlers.did_search.DIDSearchHandlerImpl', MockDIDSearchHandler)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        expected = [
            {'did': 'scope:name1', 'size': None, 'type': 'container'},
            {'did': 'scope:name2', 'size': None, 'type': 'dataset'},
            {'did': 'scope:name3', 'size': 123, 'type': 'file'}
        ]
        assert finish_json == expected, "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    rucio_api_factory = RucioAPIFactory(None)
    mocker.patch.object(rucio_api_factory, 'for_instance', return_value=rucio)
    mock_self.rucio = rucio_api_factory

    DIDSearchHandler.get(mock_self)

    calls = [call('did'), call('namespace'), call('type', 'collection')]
    mock_self.get_query_argument.assert_has_calls(calls, any_order=True)  # pylint: disable=no-member


def test_get_handler__wildcard_disabled__should_print_error(mocker, rucio):
    mock_self = MockHandler()

    def mock_get_query_argument(key, default=None):
        args = {
            'namespace': MOCK_ACTIVE_INSTANCE,
            'type': 'all',
            'did': 'scope:name'
        }
        return args.get(key, default)

    mocker.patch.object(mock_self, 'get_query_argument', side_effect=mock_get_query_argument)  # pylint: disable=no-member

    class MockDIDSearchHandler(DIDSearchHandlerImpl):
        @staticmethod
        def search_did(scope, name, search_type='all', limit=100):
            raise WildcardDisallowedException()

    mocker.patch('rucio_jupyterlab.handlers.did_search.DIDSearchHandlerImpl', MockDIDSearchHandler)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        expected = {'error': 'wildcard_disabled'}
        assert finish_json == expected, "Invalid finish response"

    mocker.patch.object(mock_self, 'set_status', return_value=None)
    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    rucio_api_factory = RucioAPIFactory(None)
    mocker.patch.object(rucio_api_factory, 'for_instance', return_value=rucio)
    mock_self.rucio = rucio_api_factory

    DIDSearchHandler.get(mock_self)

    mock_self.set_status.assert_called_with(400)  # pylint: disable=no-member
