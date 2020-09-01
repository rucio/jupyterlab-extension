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
from rucio_jupyterlab.handlers.did_details import DIDDetailsHandler
from rucio_jupyterlab.mode_handlers.replica import ReplicaModeHandler
from rucio_jupyterlab.rucio import RucioAPIFactory
from .mocks.mock_handler import MockHandler

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

    class MockReplicaModeHandler(ReplicaModeHandler):
        def get_did_details(self, scope, name, force_fetch=False):
            return mock_did_details

    mocker.patch('rucio_jupyterlab.handlers.did_details.ReplicaModeHandler', MockReplicaModeHandler)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        assert finish_json == mock_did_details, "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    DIDDetailsHandler.get(mock_self)

    calls = [call('namespace'), call('poll', '0'), call('did')]
    mock_self.get_query_argument.assert_has_calls(calls, any_order=True)  # pylint: disable=no-member
    rucio_api_factory.for_instance.assert_called_once_with(mock_active_instance)  # pylint: disable=no-member
