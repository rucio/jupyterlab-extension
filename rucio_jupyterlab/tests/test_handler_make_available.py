from .mocks.mock_handler import MockHandler
from rucio_jupyterlab.handlers.did_make_available import DIDMakeAvailableHandler
from rucio_jupyterlab.rucio import RucioAPI, RucioAPIFactory

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


def test_transfer_replica(mocker, rucio):
    mock_self = MockHandler()
    mock_self.rucio = RucioAPIFactory(None)
    rucio.instance_config = {'destination_rse': 'SWAN-EOS'}
    mocker.patch.object(mock_self.rucio, 'for_instance', return_value=rucio)
    mocker.patch.object(rucio, 'add_replication_rule', return_value={'rule_id': 'rule123'})

    DIDMakeAvailableHandler.transfer_replica(mock_self, mock_active_instance, 'scope', 'name')

    mock_self.rucio.for_instance.assert_called_once_with(mock_active_instance)

    expected_dids = [{'scope': 'scope', 'name': 'name'}]
    rucio.add_replication_rule.assert_called_once_with(dids=expected_dids, rse_expression='SWAN-EOS', copies=1)
