# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import os
import logging
import base64
import json
import psutil
from rucio_jupyterlab.rucio.client_environment import RucioClientEnvironment

download_logger = logging.getLogger('DownloadLogger')
download_logger.setLevel(logging.DEBUG)


class RucioFileDownloader:
    @staticmethod
    def start_download_target(namespace, did, rucio):
        dest_folder = RucioFileDownloader.get_dest_folder(namespace, did)

        if RucioFileDownloader.is_downloading(dest_folder):
            download_logger.debug("Other process is downloading this DID")
            return

        with RucioClientEnvironment(rucio) as rucio_home:
            os.makedirs(dest_folder, exist_ok=True)
            RucioFileDownloader.write_lockfile(dest_folder)

            try:
                results = RucioFileDownloader.download(dest_folder, did)
                RucioFileDownloader.write_donefile(dest_folder, results)
            finally:
                RucioFileDownloader.delete_lockfile(dest_folder)

    @staticmethod
    def is_downloading(dest_path):
        lockfile_path = os.path.join(dest_path, '.lockfile')

        if not os.path.isfile(lockfile_path):
            return False

        with open(lockfile_path, 'r') as lockfile:
            pid = int(lockfile.read())
            pid_exists = psutil.pid_exists(pid)

            if not pid_exists:
                return False

            process = psutil.Process(pid=pid)
            return process.is_running() and process.status() != 'zombie'

    @staticmethod
    def download(dest_path, did):
        from rucio.client import Client
        from rucio.client.downloadclient import DownloadClient

        client = Client()
        download_client = DownloadClient(client=client, logger=download_logger)

        results = download_client.download_dids([{'did': did, 'base_dir': dest_path}])

        return results

    @staticmethod
    def get_dest_folder(namespace, did):
        did_folder_name = str(base64.b32encode(did.encode('utf-8')), 'utf-8').lower().replace('=', '')
        dest_path = os.path.expanduser(os.path.join('~', 'rucio', namespace, 'downloads', did_folder_name))
        return dest_path

    @staticmethod
    def write_lockfile(dest_folder):
        file_path = os.path.join(dest_folder, '.lockfile')
        with open(file_path, 'w') as lockfile:
            content = str(os.getpid())
            lockfile.write(content)

    @staticmethod
    def delete_lockfile(dest_folder):
        file_path = os.path.join(dest_folder, '.lockfile')
        os.unlink(file_path)

    @staticmethod
    def write_donefile(dest_folder, results):
        file_path = os.path.join(dest_folder, '.donefile')
        paths = {}

        for result in results:
            scope = result['scope']
            name = result['name']
            did = scope + ':' + name
            dest_path = result['dest_file_paths'][0]
            paths[did] = dest_path

        content = json.dumps({
            'paths': paths
        })

        with open(file_path, 'w') as donefile:
            donefile.write(content)
