# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from rucio_jupyterlab.handlers.did_make_available import DIDMakeAvailableHandler
from rucio_jupyterlab.mode_handlers.replica import ReplicaModeHandler
from rucio_jupyterlab.mode_handlers.download import DownloadModeHandler
from rucio_jupyterlab.rucio import RucioAPIFactory
from .mocks.mock_handler import MockHandler

MOCK_ACTIVE_INSTANCE = 'atlas'


def test_post_handler__mode_replica(mocker, rucio):
    """
    This unit test handles the POST handler for the endpoint.
    It checks whether a query argument named 'namespace' is read,
    whether get_json_body is called, and whether set_status is
    NOT called. It also checks whether
    DIDMakeAvailableHandlerImpl.handle_make_available() is called.
    """

    mock_self = MockHandler()
    mocker.patch.object(mock_self, 'get_query_argument', return_value=MOCK_ACTIVE_INSTANCE)
    mocker.patch.object(mock_self, 'get_json_body', return_value={'did': 'scope:name'})
    mocker.patch.object(mock_self, 'set_status')

    make_available_called = False

    class MockReplicaModeHandler(ReplicaModeHandler):
        def make_available(self, scope, name):
            nonlocal make_available_called
            if scope == 'scope' and name == 'name':
                make_available_called = True
            return {}

    mocker.patch('rucio_jupyterlab.handlers.did_make_available.ReplicaModeHandler', MockReplicaModeHandler)

    rucio_api_factory = RucioAPIFactory(None)
    rucio.instance_config['mode'] = 'replica'
    mocker.patch.object(rucio_api_factory, 'for_instance', return_value=rucio)
    mock_self.rucio = rucio_api_factory

    DIDMakeAvailableHandler.post(mock_self)

    mock_self.get_query_argument.assert_called_with('namespace')  # pylint: disable=no-member
    assert make_available_called, "Make available is not called"

def test_post_handler__mode_download(mocker, rucio):
    """
    This unit test handles the POST handler for the endpoint.
    It checks whether a query argument named 'namespace' is read,
    whether get_json_body is called, and whether set_status is
    NOT called. It also checks whether
    DIDMakeAvailableHandlerImpl.handle_make_available() is called.
    """

    mock_self = MockHandler()
    mocker.patch.object(mock_self, 'get_query_argument', return_value=MOCK_ACTIVE_INSTANCE)
    mocker.patch.object(mock_self, 'get_json_body', return_value={'did': 'scope:name'})
    mocker.patch.object(mock_self, 'set_status')

    make_available_called = False

    class MockDownloadModeHandler(DownloadModeHandler):
        def make_available(self, scope, name):
            nonlocal make_available_called
            if scope == 'scope' and name == 'name':
                make_available_called = True
            return {}

    mocker.patch('rucio_jupyterlab.handlers.did_make_available.DownloadModeHandler', MockDownloadModeHandler)

    rucio_api_factory = RucioAPIFactory(None)
    rucio.instance_config['mode'] = 'download'
    mocker.patch.object(rucio_api_factory, 'for_instance', return_value=rucio)
    mock_self.rucio = rucio_api_factory

    DIDMakeAvailableHandler.post(mock_self)

    mock_self.get_query_argument.assert_called_with('namespace')  # pylint: disable=no-member
    assert make_available_called, "Make available is not called"
