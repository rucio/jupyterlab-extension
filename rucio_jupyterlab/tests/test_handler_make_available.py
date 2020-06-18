import json
from .mocks.mock_db import MockDatabaseInstance
from .mocks.mock_handler import MockHandler
from rucio_jupyterlab.handlers.did_make_available import DIDMakeAvailableHandler
import rucio_jupyterlab

mock_active_instance = 'atlas'


def test_post_handler_method_replica(mocker):
    mock_self = MockHandler()

    def mock_transfer_replica(*args, **kwargs):
        return {'rule_id': 'rule'}

    mock_self.transfer_replica = mock_transfer_replica

    mocker.patch.object(mock_self, 'get_query_argument', return_value=mock_active_instance)
    mocker.patch.object(mock_self, 'get_json_body', return_value={'did': 'scope:name', 'method': 'replica'})
    mocker.patch.object(mock_self, 'transfer_replica', side_effect=mock_transfer_replica)
    mocker.patch.object(mock_self, 'set_status')

    DIDMakeAvailableHandler.post(mock_self)

    mock_self.get_query_argument.assert_called_once_with('namespace')
    mock_self.get_json_body.assert_called_once_with()
    mock_self.transfer_replica.assert_called_once_with(mock_active_instance, 'scope', 'name')
    mock_self.set_status.assert_not_called()
