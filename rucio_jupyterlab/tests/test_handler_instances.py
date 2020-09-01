# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json
from rucio_jupyterlab.handlers.instances import InstancesHandler
from .mocks.mock_db import MockDatabaseInstance
from .mocks.mock_handler import MockHandler

MOCK_ACTIVE_INSTANCE = 'atlas'
MOCK_INSTANCES = [
    dict(name='atlas', display_name='ATLAS', rucio_base_url='https://rucio-atlas'),
    dict(name='cms', display_name='CMS', rucio_base_url='https://rucio-cms')
]


class MockRucioConfig:
    def list_instances(self):   # pylint: disable=no-self-use
        return MOCK_INSTANCES


def test_get_instances(mocker):
    mock_self = MockHandler()
    mock_db = MockDatabaseInstance()
    mock_self.rucio_config = MockRucioConfig()

    mocker.patch('rucio_jupyterlab.handlers.instances.get_db', return_value=mock_db)
    mocker.patch.object(mock_db, 'get_active_instance', return_value=MOCK_ACTIVE_INSTANCE)

    def finish_side_effect(output):
        expected_json = {
            'active_instance': MOCK_ACTIVE_INSTANCE,
            'auth_type': 'userpass',
            'instances': MOCK_INSTANCES
        }

        finish_json = json.loads(output)
        assert finish_json == expected_json, "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    InstancesHandler.get(mock_self)


def test_put_instances(mocker):
    mock_self = MockHandler()
    mock_db = MockDatabaseInstance()

    mocker.patch('rucio_jupyterlab.handlers.instances.get_db', return_value=mock_db)
    mocker.patch.object(mock_db, 'set_active_instance')
    mocker.patch.object(mock_db, 'set_active_auth_method')
    mocker.patch.object(mock_self, 'get_json_body', return_value={'instance': MOCK_ACTIVE_INSTANCE, 'auth': 'userpass'})

    InstancesHandler.put(mock_self)

    mock_db.set_active_instance.assert_called_once_with(MOCK_ACTIVE_INSTANCE)   # pylint: disable=no-member
    mock_db.set_active_auth_method.assert_called_once_with('userpass')   # pylint: disable=no-member
