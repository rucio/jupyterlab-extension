import os
from unittest.mock import patch, mock_open
import psutil
from rucio_jupyterlab.mode_handlers.download import DIDDownloader


def test_did_downloader_is_downloading__lockfile_not_exists__should_return_false(mocker):
    mocker.patch.object(os.path, 'isfile', return_value=False)
    result = DIDDownloader.is_downloading('/path')
    assert not result, 'Invalid return value'


def test_did_downloader_is_downloading__lockfile_exists__pid_not_exists__should_return_false(mocker):
    mocker.patch.object(os.path, 'isfile', return_value=True)
    mocker.patch.object(psutil, 'pid_exists', return_value=False)

    with patch("builtins.open", mock_open(read_data="123")) as mock_file:
        result = DIDDownloader.is_downloading('/path')
        assert not result, 'Invalid return value'
        mock_file.assert_called_with(os.path.join('/path', '.lockfile'), 'r')


def test_did_downloader_is_downloading__lockfile_exists__pid_exists__should_return_true(mocker):
    mocker.patch.object(os.path, 'isfile', return_value=True)
    mocker.patch.object(psutil, 'pid_exists', return_value=True)

    with patch("builtins.open", mock_open(read_data="123")) as mock_file:
        result = DIDDownloader.is_downloading('/path')
        assert result, 'Invalid return value'
        mock_file.assert_called_with(os.path.join('/path', '.lockfile'), 'r')


def test_did_downloader_write_lockfile__should_write_pid(mocker):
    mocker.patch.object(os, 'getpid', return_value=123)
    with patch("builtins.open", mock_open()) as mock_file:
        DIDDownloader.write_lockfile('/path')
        mock_file.assert_called_with(os.path.join('/path', '.lockfile'), 'w')
        mock_file.return_value.write.assert_called_once_with('123')
