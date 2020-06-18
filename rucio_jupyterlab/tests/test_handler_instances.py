import json
from .mocks.mock_db import MockDatabaseInstance
from .mocks.mock_handler import MockHandler
from rucio_jupyterlab.handlers.instances import InstancesHandler
import rucio_jupyterlab

mock_active_instance = 'atlas'
mock_instances = [
    dict(name='atlas', display_name='ATLAS', rucio_base_url='https://rucio-atlas'),
    dict(name='cms', display_name='CMS', rucio_base_url='https://rucio-cms')
]


class MockRucioConfig:
    def list_instances(self):
        return mock_instances


def test_get_instances(mocker):
    mock_self = MockHandler()
    mock_db = MockDatabaseInstance()
    mock_self.rucio_config = MockRucioConfig()

    mocker.patch('rucio_jupyterlab.handlers.instances.get_db', return_value=mock_db)
    mocker.patch.object(mock_db, 'get_active_instance', return_value=mock_active_instance)

    def finish_side_effect(str):
        global finish_json
        finish_json = json.loads(str)

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    InstancesHandler.get(mock_self)

    rucio_jupyterlab.handlers.instances.get_db.assert_called_once_with()
    mock_db.get_active_instance.assert_called_once_with()

    expected_json = {
        'active_instance': mock_active_instance,
        'instances': mock_instances
    }

    global finish_json
    assert finish_json == expected_json, "Invalid finish response"


def test_put_instances(mocker):
    mock_self = MockHandler()
    mock_db = MockDatabaseInstance()

    mocker.patch('rucio_jupyterlab.handlers.instances.get_db', return_value=mock_db)
    mocker.patch.object(mock_db, 'set_active_instance')
    mocker.patch.object(mock_self, 'get_json_body', return_value={'instance': mock_active_instance})

    InstancesHandler.put(mock_self)

    mock_db.set_active_instance.assert_called_once_with(mock_active_instance)
