# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from unittest.mock import call
from rucio_jupyterlab.kernels.ipython import RucioDIDAttachmentConnector


def test_handle_comm_message__action_inject__single_item(mocker):
    mock_msg = {
        'content': {
            'data': {
                'action': 'inject',
                'dids': [
                    {'variableName': 'var_1', 'path': '/eos/rucio/scope/name1'},
                    {'variableName': 'var_2', 'path': '/eos/rucio/scope/name2'},
                    {'variableName': 'var_3', 'path': '/eos/rucio/scope/name3'}
                ]
            }
        }
    }

    class MockIPython:
        def push(self, variables):
            pass

    class MockComm:
        ack_inject_called = False

        def __init__(self, target_name):
            pass

        def send(self, data, *args, **kwargs):  # pylint: disable=unused-argument
            if data.get('action') == 'ack-inject':
                if data.get('variable_names') == ['var_1', 'var_2', 'var_3']:
                    MockComm.ack_inject_called = True

        def on_msg(self, *args, **kwargs):
            pass

    mock_ipython = MockIPython()

    mocker.patch.object(mock_ipython, 'push')
    mocker.patch("rucio_jupyterlab.kernels.ipython.Comm", MockComm)

    connector = RucioDIDAttachmentConnector(mock_ipython)
    connector.register_outgoing_comm()
    connector.handle_comm_message(mock_msg)

    var_injection_expected_calls = [
        call({'var_1': '/eos/rucio/scope/name1'}),
        call({'var_2': '/eos/rucio/scope/name2'}),
        call({'var_3': '/eos/rucio/scope/name3'})
    ]

    mock_ipython.push.assert_has_calls(var_injection_expected_calls, any_order=True)  # pylint: disable=no-member
    assert MockComm.ack_inject_called, "Ack-inject not sent"


def test_handle_comm_message__action_inject__multiple_item(mocker):
    mock_msg = {
        'content': {
            'data': {
                'action': 'inject',
                'dids': [
                    {
                        'variableName': 'var_1',
                        'path': [
                            '/eos/rucio/scope/name1',
                            '/eos/rucio/scope/name2',
                            '/eos/rucio/scope/name3'
                        ]
                    }
                ]
            }
        }
    }

    class MockIPython:
        def push(self, variables):
            pass

    class MockComm:
        ack_inject_called = False

        def __init__(self, target_name):
            pass

        def send(self, data, *args, **kwargs):  # pylint: disable=unused-argument
            if data.get('action') == 'ack-inject':
                if data.get('variable_names') == ['var_1']:
                    MockComm.ack_inject_called = True

        def on_msg(self, *args, **kwargs):
            pass

    mock_ipython = MockIPython()

    mocker.patch.object(mock_ipython, 'push')
    mocker.patch("rucio_jupyterlab.kernels.ipython.Comm", MockComm)

    connector = RucioDIDAttachmentConnector(mock_ipython)
    connector.register_outgoing_comm()
    connector.handle_comm_message(mock_msg)

    var_injection_expected_calls = [
        call({'var_1': ['/eos/rucio/scope/name1', '/eos/rucio/scope/name2', '/eos/rucio/scope/name3']})
    ]

    mock_ipython.push.assert_has_calls(var_injection_expected_calls, any_order=True)  # pylint: disable=no-member
    assert MockComm.ack_inject_called, "Ack-inject not sent"
