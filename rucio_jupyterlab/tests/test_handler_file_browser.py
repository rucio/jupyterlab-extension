# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import os
import json
import rucio_jupyterlab.utils as utils
from rucio_jupyterlab.handlers.file_browser import FileBrowserHandler, FileBrowserHandlerImpl
from .mocks.mock_handler import MockHandler


def test_list_contents__should_ignore_dotfiles(mocker):
    def mock_listdir(_):
        return ['.abc', '.def', 'ghi']

    def mock_isfile(_):
        return True

    mocker.patch.object(os, 'listdir', side_effect=mock_listdir)
    mocker.patch.object(os.path, 'isfile', side_effect=mock_isfile)
    mocker.patch('rucio_jupyterlab.handlers.file_browser.os', os)

    result = FileBrowserHandlerImpl.list_contents('')
    file_names = utils.map(result, lambda x, _: x['name'])

    assert file_names == ['ghi'], "Not removing dotfiles"


def test_list_contents__relative_path__should_append_homedir(mocker):
    home_dir = os.path.expanduser('~')

    def mock_listdir(path):
        assert path == os.path.join(home_dir, 'path'), "Invalid path"
        return []

    mocker.patch.object(os, 'listdir', side_effect=mock_listdir)
    mocker.patch('rucio_jupyterlab.handlers.file_browser.os', os)

    FileBrowserHandlerImpl.list_contents('path')


def test_list_contents__absolute_path__should_not_append_homedir(mocker):
    def mock_listdir(path):
        assert path == '/path', "Invalid path"
        return []

    mocker.patch.object(os, 'listdir', side_effect=mock_listdir)
    mocker.patch('rucio_jupyterlab.handlers.file_browser.os', os)

    FileBrowserHandlerImpl.list_contents('/path')


def test_list_contents__path_with_tilde__should_append_homedir(mocker):
    home_dir = os.path.expanduser('~')

    def mock_listdir(path):
        assert path == os.path.join(home_dir, 'path'), "Invalid path"
        return []

    mocker.patch.object(os, 'listdir', side_effect=mock_listdir)
    mocker.patch('rucio_jupyterlab.handlers.file_browser.os', os)

    FileBrowserHandlerImpl.list_contents('~/path')


def test_list_contents__is_file_true__should_type_file(mocker):
    def mock_listdir(_):
        return ['ghi', 'jkl']

    def mock_isfile(_):
        return True

    def mock_isdir(_):
        return False

    mocker.patch.object(os, 'listdir', side_effect=mock_listdir)
    mocker.patch.object(os.path, 'isfile', side_effect=mock_isfile)
    mocker.patch.object(os.path, 'isdir', side_effect=mock_isdir)
    mocker.patch('rucio_jupyterlab.handlers.file_browser.os', os)

    result = FileBrowserHandlerImpl.list_contents('')
    types = utils.map(result, lambda x, _: x['type'])

    assert types == ['file', 'file'], "Not removing dotfiles"


def test_list_contents__is_file_false__should_type_dir(mocker):
    def mock_listdir(_):
        return ['ghi', 'jkl']

    def mock_isfile(_):
        return False

    def mock_isdir(_):
        return True

    mocker.patch.object(os, 'listdir', side_effect=mock_listdir)
    mocker.patch.object(os.path, 'isfile', side_effect=mock_isfile)
    mocker.patch.object(os.path, 'isdir', side_effect=mock_isdir)
    mocker.patch('rucio_jupyterlab.handlers.file_browser.os', os)

    result = FileBrowserHandlerImpl.list_contents('')
    types = utils.map(result, lambda x, _: x['type'])

    assert types == ['dir', 'dir'], "Not removing dotfiles"


def test_get_handler__non_empty__should_return_non_empty(mocker):
    mock_self = MockHandler()
    mocker.patch.object(mock_self, 'get_query_argument', return_value='path')

    class MockFileBrowserHandlerImpl(FileBrowserHandlerImpl):
        @staticmethod
        def list_contents(path):
            return [{'type': 'dir', 'name': 'path', 'path': '/path'}]

    mocker.patch('rucio_jupyterlab.handlers.file_browser.FileBrowserHandlerImpl', MockFileBrowserHandlerImpl)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        assert finish_json == [{'type': 'dir', 'name': 'path', 'path': '/path'}], "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    FileBrowserHandler.get(mock_self)
    mock_self.get_query_argument.assert_called_once_with('path', default='')  # pylint: disable=no-member


def test_get_handler__empty__should_return_empty(mocker):
    mock_self = MockHandler()
    mocker.patch.object(mock_self, 'get_query_argument', return_value='path')

    class MockFileBrowserHandlerImpl(FileBrowserHandlerImpl):
        @staticmethod
        def list_contents(path):
            return []

    mocker.patch('rucio_jupyterlab.handlers.file_browser.FileBrowserHandlerImpl', MockFileBrowserHandlerImpl)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        assert finish_json == [], "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    FileBrowserHandler.get(mock_self)
    mock_self.get_query_argument.assert_called_once_with('path', default='')  # pylint: disable=no-member


def test_get_handler__not_exists__should_return_error(mocker):
    mock_self = MockHandler()
    mocker.patch.object(mock_self, 'get_query_argument', return_value='path')

    class MockFileBrowserHandlerImpl(FileBrowserHandlerImpl):
        @staticmethod
        def list_contents(path):
            return None

    mocker.patch('rucio_jupyterlab.handlers.file_browser.FileBrowserHandlerImpl', MockFileBrowserHandlerImpl)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        assert finish_json == {'success': False}, "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)
    FileBrowserHandler.get(mock_self)
    mock_self.get_query_argument.assert_called_once_with('path', default='')  # pylint: disable=no-member
