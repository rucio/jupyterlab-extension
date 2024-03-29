# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021

import os
from unittest.mock import patch, mock_open
import psutil
from rucio_jupyterlab.rucio.download import RucioFileDownloader


def test_rucio_file_downloader_is_downloading__lockfile_not_exists__should_return_false(mocker):
    mocker.patch.object(os.path, 'isfile', return_value=False)
    result = RucioFileDownloader.is_downloading('/path')
    assert not result, 'Invalid return value'


def test_rucio_file_downloader_is_downloading__lockfile_exists__pid_not_exists__should_return_false(mocker):
    mocker.patch.object(os.path, 'isfile', return_value=True)
    mocker.patch.object(psutil, 'pid_exists', return_value=False)

    with patch("builtins.open", mock_open(read_data="123")) as mock_file:
        result = RucioFileDownloader.is_downloading('/path')
        assert not result, 'Invalid return value'
        mock_file.assert_called_with(os.path.join('/path', '.lockfile'), 'r')


def test_rucio_file_downloader_is_downloading__lockfile_exists__pid_exists__process_not_running__should_return_false(mocker):
    mocker.patch.object(os.path, 'isfile', return_value=True)
    mocker.patch.object(psutil, 'pid_exists', return_value=True)

    class MockProcess:
        def __init__(self, pid):
            pass

        def is_running(self):   # pylint: disable=no-self-use
            return False

        def status(self):   # pylint: disable=no-self-use
            return 'running'

    mocker.patch('rucio_jupyterlab.rucio.download.psutil.Process', MockProcess)

    with patch("builtins.open", mock_open(read_data="123")) as mock_file:
        result = RucioFileDownloader.is_downloading('/path')
        assert not result, 'Invalid return value'
        mock_file.assert_called_with(os.path.join('/path', '.lockfile'), 'r')


def test_rucio_file_downloader_is_downloading__lockfile_exists__pid_exists__process_running__status_running__should_return_true(mocker):
    mocker.patch.object(os.path, 'isfile', return_value=True)
    mocker.patch.object(psutil, 'pid_exists', return_value=True)

    class MockProcess:
        def __init__(self, pid):
            pass

        def is_running(self):   # pylint: disable=no-self-use
            return True

        def status(self):   # pylint: disable=no-self-use
            return 'running'

    mocker.patch('rucio_jupyterlab.rucio.download.psutil.Process', MockProcess)

    with patch("builtins.open", mock_open(read_data="123")) as mock_file:
        result = RucioFileDownloader.is_downloading('/path')
        assert result, 'Invalid return value'
        mock_file.assert_called_with(os.path.join('/path', '.lockfile'), 'r')


def test_rucio_file_downloader_is_downloading__lockfile_exists__pid_exists__process_running__status_zombie__should_return_false(mocker):
    mocker.patch.object(os.path, 'isfile', return_value=True)
    mocker.patch.object(psutil, 'pid_exists', return_value=True)

    class MockProcess:
        def __init__(self, pid):
            pass

        def is_running(self):   # pylint: disable=no-self-use
            return True

        def status(self):   # pylint: disable=no-self-use
            return 'zombie'

    mocker.patch('rucio_jupyterlab.rucio.download.psutil.Process', MockProcess)

    with patch("builtins.open", mock_open(read_data="123")) as mock_file:
        result = RucioFileDownloader.is_downloading('/path')
        assert not result, 'Invalid return value'
        mock_file.assert_called_with(os.path.join('/path', '.lockfile'), 'r')


def test_rucio_file_downloader_write_lockfile__should_write_pid(mocker):
    mocker.patch.object(os, 'getpid', return_value=123)
    with patch("builtins.open", mock_open()) as mock_file:
        RucioFileDownloader.write_lockfile('/path')
        mock_file.assert_called_with(os.path.join('/path', '.lockfile'), 'w')
        mock_file.return_value.write.assert_called_once_with('123')
