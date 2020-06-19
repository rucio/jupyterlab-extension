import pytest
from .mocks.mock_handler import MockHandler
from rucio_jupyterlab.handlers.did_make_available import DIDMakeAvailableHandler, DIDMakeAvailableHandlerImpl, UnknownMethodException
from rucio_jupyterlab.rucio import RucioAPI, RucioAPIFactory

mock_active_instance = 'atlas'


def test_handle_make_available__method_replica(mocker, rucio):
    """
    Method handle_make_available() should call add_replication_rule
    if the given method is replica. Additionally, it should pass the
    split scope and name to the called method.
    """

    mocker.patch.dict(rucio.instance_config, {'destination_rse': 'SWAN-EOS'})
    mocker.patch.object(rucio, 'add_replication_rule', return_value={})

    handler = DIDMakeAvailableHandlerImpl(mock_active_instance, rucio)
    handler.handle_make_available('scope:name', 'replica')

    expected_dids = [{'scope': 'scope', 'name': 'name'}]
    rucio.add_replication_rule.assert_called_once_with(dids=expected_dids, rse_expression='SWAN-EOS', copies=1)


def test_handle_make_available__method_unknown(mocker, rucio):
    """
    Method handle_make_available() should raise an exception if
    the method is unknown.
    """

    mocker.patch.dict(rucio.instance_config, {'destination_rse': 'SWAN-EOS'})
    mocker.patch.object(rucio, 'add_replication_rule', return_value={})

    with pytest.raises(UnknownMethodException) as exc:
        handler = DIDMakeAvailableHandlerImpl(mock_active_instance, rucio)
        handler.handle_make_available('scope:name', 'blablablabla')


def test_post_handler__method_replica(mocker, rucio):
    """
    This unit test handles the POST handler for the endpoint.
    It checks whether a query argument named 'namespace' is read,
    whether get_json_body is called, and whether set_status is
    NOT called. It also checks whether 
    DIDMakeAvailableHandlerImpl.handle_make_available() is called.
    """

    mock_self = MockHandler()
    mocker.patch.object(mock_self, 'get_query_argument', return_value=mock_active_instance)
    mocker.patch.object(mock_self, 'get_json_body', return_value={'did': 'scope:name', 'method': 'replica'})
    mocker.patch.object(mock_self, 'set_status')

    global make_available_called
    make_available_called = False

    class MockDIDMakeAvailableHandlerImpl(DIDMakeAvailableHandlerImpl):
        def handle_make_available(self, did, method, *args, **kwargs):
            global make_available_called
            if did == 'scope:name' and method == 'replica':
                make_available_called = True
            return {}

    mocker.patch('rucio_jupyterlab.handlers.did_make_available.DIDMakeAvailableHandlerImpl', MockDIDMakeAvailableHandlerImpl)

    rucio_api_factory = RucioAPIFactory(None)
    mocker.patch.object(rucio_api_factory, 'for_instance', return_value=rucio)
    mock_self.rucio = rucio_api_factory

    DIDMakeAvailableHandler.post(mock_self)

    mock_self.get_query_argument.assert_called_with('namespace')
    mock_self.get_json_body.assert_called_once_with()
    mock_self.set_status.assert_not_called()

    assert make_available_called, "Make available is not called"


def test_post_handler__method_unknown(mocker, rucio):
    """
    This unit test handles the POST handler for the endpoint.
    It checks whether set_status is called if an exception is raised.
    """

    mock_self = MockHandler()
    mocker.patch.object(mock_self, 'get_query_argument', return_value=mock_active_instance)
    mocker.patch.object(mock_self, 'get_json_body', return_value={'did': 'scope:name', 'method': 'lalalalalal'})
    mocker.patch.object(mock_self, 'set_status')

    class MockDIDMakeAvailableHandlerImpl(DIDMakeAvailableHandlerImpl):
        def handle_make_available(self, did, method, *args, **kwargs):
            raise UnknownMethodException()

    mocker.patch('rucio_jupyterlab.handlers.did_make_available.DIDMakeAvailableHandlerImpl', MockDIDMakeAvailableHandlerImpl)

    rucio_api_factory = RucioAPIFactory(None)
    mocker.patch.object(rucio_api_factory, 'for_instance', return_value=rucio)
    mock_self.rucio = rucio_api_factory

    DIDMakeAvailableHandler.post(mock_self)
    mock_self.set_status.assert_called_with(400)
