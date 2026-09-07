# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import os
import json
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
    mocker.patch.object(os, 'makedirs', return_value=None)

    # Mock low-level file operations
    mock_os_open = mocker.patch('os.open', return_value=3)  # 3 = fake file descriptor
    mock_os_fdopen = mocker.patch('os.fdopen')

    # Create a mock file object
    mock_file = mocker.MagicMock()
    mock_os_fdopen.return_value = mock_file
    mock_file.__enter__.return_value = mock_file  # For context manager

    # Call the function
    result = RucioFileDownloader.write_lockfile('/path')

    # Verify file operations
    lockfile_path = os.path.join('/path', '.lockfile')
    mock_os_open.assert_called_once_with(
        lockfile_path,
        os.O_CREAT | os.O_EXCL | os.O_WRONLY
    )
    mock_os_fdopen.assert_called_once_with(3, 'w')
    mock_file.write.assert_called_once_with('123')

    # Verify return value
    assert result is True


# --- Failure diagnostics -------------------------------------------------
#
# These failures are opaque in practice: a wrong `vo` is only ever exercised by the
# download client (the API path authenticates without a VO), and a missing gfal2 shows
# up as a generic "no files downloaded". Both cost real debugging time, so the cause is
# attached to the error file the UI reads.

class CannotAuthenticate(Exception):
    pass


class MissingDependency(Exception):
    pass


class NoFilesDownloaded(Exception):
    pass


def test_diagnose_cannot_authenticate_mentions_configured_vo():
    hint = RucioFileDownloader.diagnose(CannotAuthenticate('Cannot authenticate.'), {'vo': 'escape'})
    assert hint is not None, "CannotAuthenticate with a configured vo must produce a hint"
    assert "vo='escape'" in hint, "Hint must name the configured vo"


def test_diagnose_cannot_authenticate_without_vo_gives_no_vo_hint():
    hint = RucioFileDownloader.diagnose(CannotAuthenticate('Cannot authenticate.'), {})
    assert hint is None, "Without a configured vo there is no vo-related hint to give"


def test_diagnose_missing_dependency_mentions_gfal2():
    hint = RucioFileDownloader.diagnose(MissingDependency('One dependency is missing.'), {})
    assert hint is not None and 'gfal2' in hint, "MissingDependency must point at the transfer library"


def test_diagnose_no_files_downloaded_is_actionable():
    hint = RucioFileDownloader.diagnose(NoFilesDownloaded('None of the requested files have been downloaded.'), {})
    assert hint is not None and 'gfal2' in hint, "NoFilesDownloaded must suggest the usual causes"


def test_diagnose_missing_oidc_token_is_actionable():
    hint = RucioFileDownloader.diagnose(RuntimeError('No OIDC token available for the download client.'), {})
    assert hint is not None and 'OIDC' in hint, "A missing OIDC token must point at re-authenticating"


def test_diagnose_oidc_token_error_is_actionable():
    hint = RucioFileDownloader.diagnose(RuntimeError('Could not obtain an OIDC token for the download client: boom'), {})
    assert hint is not None and 'OIDC' in hint, "An OIDC token retrieval failure must point at re-authenticating"


def test_diagnose_unknown_exception_returns_none():
    assert RucioFileDownloader.diagnose(ValueError('something else'), {'vo': 'escape'}) is None


def test_write_errorfile_embeds_hint(tmp_path):
    dest = str(tmp_path / 'dl')
    RucioFileDownloader.write_errorfile(dest, CannotAuthenticate('Cannot authenticate.'), {'vo': 'escape'})
    with open(os.path.join(dest, 'error.json')) as f:
        payload = json.load(f)
    assert 'hint' in payload, "error.json must carry the hint for the UI"
    assert "vo='escape'" in payload['exception_message'], "Message shown to the user must include the hint"
