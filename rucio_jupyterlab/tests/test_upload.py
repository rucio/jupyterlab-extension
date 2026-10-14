# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

import pytest

from rucio_jupyterlab.handlers.upload import UploadHandler, UploadHandlerImpl, UploadValidationError
from rucio_jupyterlab.rucio import upload as upload_module
from rucio_jupyterlab.rucio.upload import RucioFileUploader


def valid_upload_body(**overrides):
    body = {
        'file_paths': ['/tmp/one', '/tmp/two'],
        'rse': 'RSE',
        'scope': 'scope',
    }
    body.update(overrides)
    return body


class FakeDB:
    def __init__(self):
        self.calls = []
        self.next_id = 1
        self.finished = []

    def add_upload_job(self, **kwargs):
        self.calls.append(kwargs)
        job_id = self.next_id
        self.next_id += 1
        return job_id

    def mark_upload_job_finished(self, job_id):
        self.finished.append(job_id)


@pytest.mark.parametrize('file_paths', [None, [], [''], [1], ['/tmp/one', '']])
def test_upload_request_rejects_invalid_file_paths(file_paths):
    with pytest.raises(UploadValidationError):
        UploadHandler._parse_upload_request(valid_upload_body(file_paths=file_paths))


@pytest.mark.parametrize('field,value', [
    ('rse', None),
    ('rse', 1),
    ('rse', ''),
    ('rse', '   '),
    ('scope', None),
    ('scope', 1),
    ('scope', ''),
    ('scope', '   '),
])
def test_upload_request_rejects_invalid_rse_or_scope(field, value):
    with pytest.raises(UploadValidationError):
        UploadHandler._parse_upload_request(valid_upload_body(**{field: value}))


@pytest.mark.parametrize('lifetime', [True, False, 1.5, '60', -1])
def test_upload_request_rejects_invalid_lifetime(lifetime):
    with pytest.raises(UploadValidationError):
        UploadHandler._parse_upload_request(valid_upload_body(lifetime=lifetime))


@pytest.mark.parametrize('lifetime,expected_lifetime', [('', None), (60, 60)])
def test_upload_request_normalizes_values(lifetime, expected_lifetime):
    file_paths = ['/tmp/one', '/tmp/two']
    result = UploadHandler._parse_upload_request(valid_upload_body(
        file_paths=file_paths,
        rse='  RSE  ',
        scope='  scope  ',
        lifetime=lifetime,
    ))

    assert result == (file_paths, 'RSE', 'scope', None, None, expected_lifetime)


@pytest.mark.parametrize(
    'dataset_scope,dataset_name',
    [(None, 'dataset'), ('dataset_scope', None), ('', 'dataset'), ('dataset_scope', '')]
)
def test_upload_request_requires_both_dataset_fields(dataset_scope, dataset_name):
    with pytest.raises(UploadValidationError):
        UploadHandler._parse_upload_request(valid_upload_body(
            add_to_dataset=True,
            dataset_scope=dataset_scope,
            dataset_name=dataset_name,
        ))


def test_upload_request_rejects_lifetime_for_dataset_upload():
    with pytest.raises(UploadValidationError):
        UploadHandler._parse_upload_request(valid_upload_body(
            add_to_dataset=True,
            dataset_scope='dataset_scope',
            dataset_name='dataset',
            lifetime=60,
        ))


def test_upload_request_clears_dataset_fields_when_dataset_mode_is_false():
    result = UploadHandler._parse_upload_request(valid_upload_body(
        dataset_scope='ignored_scope',
        dataset_name='ignored_name',
    ))

    assert result[3:5] == (None, None)


def test_upload_handler_impl_starts_one_ordered_batch_process(mocker):
    process = mocker.Mock(pid=123)
    process_factory = mocker.patch('rucio_jupyterlab.handlers.upload.mp.Process', return_value=process)
    paths = ['/tmp/first', '/tmp/second']

    UploadHandlerImpl.upload('namespace', 'rucio', paths, 'RSE', 'scope')

    process_factory.assert_called_once_with(
        target=RucioFileUploader.start_upload_batch_target,
        args=('namespace', 'rucio', paths, 'RSE', 'scope', None, None, None),
    )
    process.start.assert_called_once_with()


def test_upload_handler_impl_propagates_process_start_error(mocker):
    process = mocker.Mock(pid=123)
    process.start.side_effect = OSError('cannot start')
    mocker.patch('rucio_jupyterlab.handlers.upload.mp.Process', return_value=process)

    with pytest.raises(OSError, match='cannot start'):
        UploadHandlerImpl.upload('namespace', 'rucio', ['/tmp/file'], 'RSE', 'scope')


def test_batch_target_continues_after_file_failure(mocker):
    environment = mocker.patch('rucio_jupyterlab.rucio.upload.RucioClientEnvironment')
    mocker.patch.object(RucioFileUploader, '__init__', return_value=None)
    upload = mocker.patch.object(
        RucioFileUploader,
        'upload',
        side_effect=[RuntimeError('first file failed'), None, None],
    )

    RucioFileUploader.start_upload_batch_target(
        'namespace', 'rucio', ['/tmp/first', '/tmp/second', '/tmp/third'], 'RSE', 'scope'
    )

    environment.assert_called_once_with('rucio')
    assert [call.kwargs['file_path'] for call in upload.call_args_list] == [
        '/tmp/first', '/tmp/second', '/tmp/third'
    ]


def test_upload_logger_cleanup_preserves_failed_log_and_removes_success_log(mocker, tmp_path):
    uploader = RucioFileUploader.__new__(RucioFileUploader)
    uploader.namespace = 'namespace'
    uploader.db = FakeDB()
    mocker.patch.object(upload_module, 'LOGFILE_DIR', str(tmp_path))
    client = mocker.patch('rucio.client.uploadclient.UploadClient')
    client.return_value.upload.side_effect = [RuntimeError('failed'), 0]

    uploader.upload('/tmp/failed', 'RSE', 'scope')
    uploader.upload('/tmp/success', 'RSE', 'scope')

    failed_log = tmp_path / '1.log'
    assert failed_log.exists()
    assert 'Upload failed' in failed_log.read_text()
    assert not (tmp_path / '2.log').exists()
    loggers = [call.kwargs['logger'] for call in client.call_args_list]
    assert loggers[0] is not loggers[1]
    assert not loggers[0].handlers
    assert not loggers[1].handlers
    assert uploader.db.finished == [2]


@pytest.mark.parametrize('failing_call', ['os.makedirs', 'logging.FileHandler'])
def test_upload_logs_setup_failure_to_stream(mocker, tmp_path, capsys, failing_call):
    uploader = RucioFileUploader.__new__(RucioFileUploader)
    uploader.namespace = 'namespace'
    uploader.db = FakeDB()
    mocker.patch.object(upload_module, 'LOGFILE_DIR', str(tmp_path / 'logs'))
    mocker.patch(f'rucio_jupyterlab.rucio.upload.{failing_call}', side_effect=OSError('log setup failed'))
    client = mocker.patch('rucio.client.uploadclient.UploadClient')
    upload_logger = upload_module.logging.getLogger('UploadLogger.1')
    handlers_before = list(upload_logger.handlers)

    uploader.upload('/tmp/file', 'RSE', 'scope')

    stderr = capsys.readouterr().err
    assert 'Upload failed' in stderr
    assert 'log setup failed' in stderr
    client.assert_not_called()
    assert uploader.db.finished == []
    assert upload_logger.handlers == handlers_before


def test_add_upload_job_requires_both_dataset_parts_for_dataset_did():
    uploader = RucioFileUploader.__new__(RucioFileUploader)
    uploader.namespace = 'namespace'
    uploader.db = FakeDB()

    uploader.add_upload_job('/tmp/file', 'RSE', 'scope', dataset_scope='dataset_scope')
    uploader.add_upload_job('/tmp/file', 'RSE', 'scope', dataset_name='dataset_name')
    uploader.add_upload_job('/tmp/file', 'RSE', 'scope', dataset_scope='dataset_scope', dataset_name='dataset_name')

    assert [call['dataset_did'] for call in uploader.db.calls] == [None, None, 'dataset_scope:dataset_name']
