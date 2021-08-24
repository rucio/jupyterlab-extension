# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import os
import multiprocessing as mp
import json
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile
import rucio_jupyterlab.utils as utils
from rucio_jupyterlab.rucio.download import RucioFileDownloader

BASE_DIR = '~/rucio/downloads'


class DownloadModeHandler:
    STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
    STATUS_REPLICATING = "REPLICATING"
    STATUS_OK = "OK"
    STATUS_STUCK = "STUCK"

    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name

    def make_available(self, scope, name):
        did = scope + ':' + name
        paths = self._get_file_paths(did)
        if paths is not None:
            unavailable_did = utils.find(lambda x: not os.path.isfile(paths[x]), paths)
            if unavailable_did is None:
                return

        process = mp.Process(target=RucioFileDownloader.start_download_target, args=(self.namespace, did, self.rucio))
        process.start()

    def get_did_details(self, scope, name, force_fetch=False):
        did = scope + ':' + name
        attached_files = self._get_attached_files(scope, name, force_fetch)

        dest_dir_exists = self._dest_dir_exists(did)
        is_downloading = self._is_downloading(did)
        paths = self._get_file_paths(did)

        def result_mapper(file, _):
            if not dest_dir_exists:
                return dict(status=DownloadModeHandler.STATUS_NOT_AVAILABLE, did=file.did, path=None, size=file.size)

            if is_downloading:
                return dict(status=DownloadModeHandler.STATUS_REPLICATING, did=file.did, path=None, size=file.size)

            if not paths:
                return dict(status=DownloadModeHandler.STATUS_STUCK, did=file.did, path=None, size=file.size)

            path = paths.get(file.did)

            if not os.path.isfile(path):
                return dict(status=DownloadModeHandler.STATUS_STUCK, did=file.did, path=None, size=file.size)

            return dict(status=DownloadModeHandler.STATUS_OK, did=file.did, path=path, size=file.size)

        results = utils.map(attached_files, result_mapper)
        return results

    def _get_attached_files(self, scope, name, force_fetch=False):
        did = scope + ':' + name
        attached_files = self.db.get_attached_files(self.namespace, did) if not force_fetch else None
        if not attached_files:
            rucio_attached_files = self.rucio.get_files(scope, name)

            def mapper(d, _):
                return AttachedFile(did=(d.get('scope') + ':' + d.get('name')), size=d.get('bytes'))

            attached_files = utils.map(rucio_attached_files, mapper)

        return attached_files

    def _is_downloading(self, did):
        dest_path = RucioFileDownloader.get_dest_folder(self.namespace, did)
        return RucioFileDownloader.is_downloading(dest_path)

    def _dest_dir_exists(self, did):
        dest_path = RucioFileDownloader.get_dest_folder(self.namespace, did)
        return os.path.isdir(dest_path)

    def _did_path_exists(self, did):
        dest_path = RucioFileDownloader.get_dest_folder(self.namespace, did)
        return os.path.isdir(dest_path)

    def _get_file_paths(self, did):
        dest_path = RucioFileDownloader.get_dest_folder(self.namespace, did)
        donefile_path = os.path.join(dest_path, '.donefile')

        if not os.path.isfile(donefile_path):
            return None

        with open(donefile_path, 'r') as donefile:
            content = donefile.read()
            data = json.loads(content)
            paths = data.get('paths')
            return paths
