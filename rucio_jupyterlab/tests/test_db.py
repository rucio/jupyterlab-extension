# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json
import time
import pytest
from rucio_jupyterlab.db import DatabaseInstance
from rucio_jupyterlab.entity import AttachedFile
from .mocks.mock_db import Struct


@pytest.fixture
def database_instance():
    return DatabaseInstance()


def test_get_config__config_exists(database_instance, mocker):  # pylint: disable=redefined-outer-name
    class MockUserConfig:
        key = 'key'

        @staticmethod
        def get_or_none(*args, **kwargs):  # pylint: disable=unused-argument
            return Struct(key='key', value='value')

    mocker.patch('rucio_jupyterlab.db.UserConfig', MockUserConfig)
    result = database_instance.get_config('key')

    assert result == 'value', "Invalid return value"


def test_get_config__config_not_exists(database_instance, mocker):  # pylint: disable=redefined-outer-name
    class MockUserConfig:
        key = 'key'

        @staticmethod
        def get_or_none(*args, **kwargs):  # pylint: disable=unused-argument
            return None

    mocker.patch('rucio_jupyterlab.db.UserConfig', MockUserConfig)
    result = database_instance.get_config('key')

    assert result is None, "Return value should be None"


def test_get_attached_files__files_exist(database_instance, mocker):  # pylint: disable=redefined-outer-name
    class MockAttachedFilesListCache:
        namespace = 'namespace'
        did = 'did'
        expiry = 0

        @staticmethod
        def get_or_none(*args, **kwargs):  # pylint: disable=unused-argument
            file_dids = [
                {'did': 'did1', 'size': 1},
                {'did': 'did2', 'size': 3}
            ]
            file_dids_json = json.dumps(file_dids)
            return Struct(file_dids=file_dids_json)

    mocker.patch('rucio_jupyterlab.db.AttachedFilesListCache', MockAttachedFilesListCache)
    result = database_instance.get_attached_files('namespace', 'did')
    result_dict = [x.__dict__ for x in result]

    expected_result = [
        AttachedFile(did='did1', size=1),
        AttachedFile(did='did2', size=3)
    ]
    expected_result_dict = [x.__dict__ for x in expected_result]

    assert result_dict == expected_result_dict, "Invalid return value"

    for res in result:
        assert isinstance(res, AttachedFile), "Return array element is not AttachedFile"


def test_get_attached_files__files_not_exist(database_instance, mocker):  # pylint: disable=redefined-outer-name
    class MockAttachedFilesListCache:
        namespace = 'namespace'
        did = 'did'
        expiry = 0

        @staticmethod
        def get_or_none(*args, **kwargs):  # pylint: disable=no-self-use,unused-argument
            return None

    mocker.patch('rucio_jupyterlab.db.AttachedFilesListCache', MockAttachedFilesListCache)
    result = database_instance.get_attached_files('namespace', 'did')

    assert result is None, "Invalid return value"


def test_set_attached_files(database_instance, mocker):  # pylint: disable=redefined-outer-name
    class MockAttachedFilesListCache:
        @staticmethod
        def execute(*args, **kwargs):  # pylint: disable=unused-argument
            pass

        @staticmethod
        def replace(namespace, did, file_dids, expiry):
            assert namespace == 'namespace', "Invalid namespace"
            assert did == 'scope:name', "Invalid DID"
            expected_file_dids = [
                {'did': 'did1', 'size': 1},
                {'did': 'did2', 'size': 3}
            ]

            assert json.loads(file_dids) == expected_file_dids, "Invalid file DIDs"
            assert expiry > int(time.time()), "Expiry should be later than current time"

            return MockAttachedFilesListCache

    mocker.patch('rucio_jupyterlab.db.AttachedFilesListCache', MockAttachedFilesListCache)

    attached_files = [
        AttachedFile(did='did1', size=1),
        AttachedFile(did='did2', size=3)
    ]
    database_instance.set_attached_files('namespace', 'scope:name', attached_files)


def test_set_file_replica(database_instance, mocker):  # pylint: disable=redefined-outer-name
    class MockFileReplicasCache:
        @staticmethod
        def execute(*args, **kwargs):  # pylint: disable=unused-argument
            pass

        @staticmethod
        def replace(namespace, did, pfn, size, expiry, *args, **kwargs):  # pylint: disable=unused-argument
            assert namespace == 'namespace', "Invalid namespace"
            assert did == 'scope:name', "Invalid DID"
            assert pfn == 'root://xrd1:1094//test', "Invalid PFN"
            assert size == 123, "Invalid size"
            assert expiry > int(time.time()), "Expiry should be later than current time"

            return MockFileReplicasCache

    mocker.patch('rucio_jupyterlab.db.FileReplicasCache', MockFileReplicasCache)

    database_instance.set_file_replica('namespace', 'scope:name', 'root://xrd1:1094//test', 123)


def test_purge_cache(database_instance, mocker):  # pylint: disable=redefined-outer-name
    class MockDeleteQuery:
        @staticmethod
        def execute(*args, **kwargs):
            pass

    class MockCacheEntity:
        def __init__(self):
            self.called = False

        def delete(self, *args, **kwargs):  # pylint: disable=unused-argument
            self.called = True
            return MockDeleteQuery

    mock_replicas_cache = MockCacheEntity()
    mock_attached_files_list_cache = MockCacheEntity()

    mocker.patch('rucio_jupyterlab.db.FileReplicasCache', mock_replicas_cache)
    mocker.patch('rucio_jupyterlab.db.AttachedFilesListCache', mock_attached_files_list_cache)

    database_instance.purge_cache()

    assert mock_replicas_cache.called, "FileReplicasCache not cleared"
    assert mock_attached_files_list_cache.called, "AttachedFilesListCache not cleared"
