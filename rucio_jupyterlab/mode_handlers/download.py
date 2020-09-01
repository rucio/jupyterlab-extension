# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import os
import tempfile
import logging
import multiprocessing as mp
import traceback
import base64
import json
from shutil import copyfile, which
import subprocess
import psutil
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile
import rucio_jupyterlab.utils as utils

download_logger = logging.getLogger('DownloadLogger')
download_logger.setLevel(logging.DEBUG)

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

        config = self._get_config()
        auth_type = self.rucio.auth_type
        auth_config = self.rucio.auth_config
        instance_config = self.rucio.instance_config
        process = mp.Process(target=DIDDownloader.start_download_target, args=(self.namespace, did, config, instance_config, auth_type, auth_config))
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

    def _get_config(self):
        instance_config = self.rucio.instance_config
        base_url = self.rucio.base_url
        auth_config = self.rucio.auth_config
        auth_type = self.rucio.auth_type
        auth_url = self.rucio.auth_url

        cert_path = auth_config.get('certificate')
        key_path = auth_config.get('key')
        username = auth_config.get('username')
        password = auth_config.get('password')
        account = auth_config.get('account')

        config = {
            'rucio_host': base_url,
            'auth_host': auth_url,
            'auth_type': auth_type,
            'username': username,
            'password': password,
            'client_cert': cert_path,
            'client_key': key_path,
            'account': account,
            'ca_cert': instance_config.get('rucio_ca_cert')
        }

        vo = instance_config.get('vo')  # pylint: disable=invalid-name
        if vo is not None:
            config['vo'] = vo

        return config

    def _is_downloading(self, did):
        dest_path = DIDDownloader.get_dest_folder(self.namespace, did)
        return DIDDownloader.is_downloading(dest_path)

    def _dest_dir_exists(self, did):
        dest_path = DIDDownloader.get_dest_folder(self.namespace, did)
        return os.path.isdir(dest_path)

    def _did_path_exists(self, did):
        dest_path = DIDDownloader.get_dest_folder(self.namespace, did)
        return os.path.isdir(dest_path)

    def _get_file_paths(self, did):
        dest_path = DIDDownloader.get_dest_folder(self.namespace, did)
        donefile_path = os.path.join(dest_path, '.donefile')

        if not os.path.isfile(donefile_path):
            return None

        with open(donefile_path, 'r') as donefile:
            content = donefile.read()
            data = json.loads(content)
            paths = data.get('paths')
            return paths


class DIDDownloader:
    @staticmethod
    def start_download_target(namespace, did, config, instance_config, auth_type=None, auth_config=None):
        dest_folder = DIDDownloader.get_dest_folder(namespace, did)

        if DIDDownloader.is_downloading(dest_folder):
            download_logger.debug("Other process is downloading this DID")
            return

        with tempfile.TemporaryDirectory() as rucio_home:
            download_logger.debug("Creating temporary directory: %s", rucio_home)

            site_name = instance_config.get("site_name")
            if site_name is not None:
                os.environ['SITE_NAME'] = site_name

            os.environ['RUCIO_HOME'] = rucio_home
            DIDDownloader.write_temp_config_file(rucio_home, config)

            os.makedirs(dest_folder, exist_ok=True)
            DIDDownloader.write_lockfile(dest_folder)

            if auth_config is not None:
                if auth_type == 'x509':
                    DIDDownloader.prepare_x509_user_authentication(rucio_home, instance_config=instance_config, auth_config=auth_config)
                elif auth_type == 'x509_proxy':
                    DIDDownloader.prepare_x509_proxy_authentication(rucio_home, auth_config=auth_config)

            try:
                results = DIDDownloader.download(dest_folder, did)
                DIDDownloader.write_donefile(dest_folder, results)
            finally:
                DIDDownloader.delete_lockfile(dest_folder)

    @staticmethod
    def prepare_x509_user_authentication(rucio_home, instance_config, auth_config):
        cert_path = auth_config.get('certificate')
        key_path = auth_config.get('key')
        voms_nickname = instance_config.get('vo')
        voms_enabled = instance_config.get('voms_enabled', False)
        voms_certdir_path = instance_config.get('voms_certdir_path')
        voms_vomsdir_path = instance_config.get('voms_vomsdir_path')
        voms_vomses_path = instance_config.get('voms_vomses_path')

        if cert_path and key_path:
            tmp_cert_path, tmp_key_path = DIDDownloader.write_user_certificate_files(rucio_home, cert_path, key_path)
            tmp_proxy_path = DIDDownloader.generate_proxy_certificate(
                rucio_home,
                tmp_cert_path,
                tmp_key_path,
                voms_enabled=voms_enabled,
                voms_nickname=voms_nickname,
                voms_certdir_path=voms_certdir_path,
                voms_vomsdir_path=voms_vomsdir_path,
                voms_vomses_path=voms_vomses_path
            )

            if tmp_proxy_path is not None:
                os.environ['X509_USER_PROXY'] = tmp_proxy_path

            if tmp_cert_path is not None and tmp_key_path is not None:
                os.environ['X509_USER_CERT'] = tmp_cert_path
                os.environ['X509_USER_KEY'] = tmp_key_path

    @staticmethod
    def prepare_x509_proxy_authentication(rucio_home, auth_config):
        proxy_path = auth_config.get('proxy')

        if proxy_path:
            tmp_proxy_path = DIDDownloader.write_proxy_certificate_files(rucio_home, proxy_path)
            if tmp_proxy_path is not None:
                os.environ['X509_USER_PROXY'] = tmp_proxy_path

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
    def write_temp_config_file(base_dir, config):
        lines = ['[client]\n'] + [f'{x}={config[x]}\n' for x in config]

        etc_path = os.path.join(base_dir, 'etc')
        cfg_path = os.path.join(etc_path, 'rucio.cfg')
        os.makedirs(etc_path, exist_ok=True)

        config_file = open(cfg_path, 'w')
        config_file.writelines(lines)
        config_file.close()

    @staticmethod
    def write_user_certificate_files(base_dir, cert_path, key_path):
        dest_cert_path = os.path.join(base_dir, 'usercert.pem')
        dest_key_path = os.path.join(base_dir, 'userkey.pem')

        copyfile(cert_path, dest_cert_path)
        copyfile(key_path, dest_key_path)

        os.chmod(dest_cert_path, 0o400)
        os.chmod(dest_key_path, 0o400)

        return dest_cert_path, dest_key_path

    @staticmethod
    def write_proxy_certificate_files(base_dir, proxy_path):
        dest_proxy_path = os.path.join(base_dir, 'proxy.pem')
        copyfile(proxy_path, dest_proxy_path)
        os.chmod(dest_proxy_path, 0o400)
        return dest_proxy_path

    @staticmethod
    def generate_proxy_certificate(base_dir, cert_path, key_path, voms_enabled=False, voms_nickname=None, voms_certdir_path=None, voms_vomsdir_path=None, voms_vomses_path=None):
        dest_proxy_path = os.path.join(base_dir, 'x509up')
        cmd_args = {
            '-cert': cert_path,
            '-key': key_path,
            '-out': dest_proxy_path
        }

        if which('voms-proxy-init') is not None:
            executable = "voms-proxy-init"

            if voms_enabled:
                if voms_nickname is not None:
                    cmd_args['--voms'] = voms_nickname

                if voms_certdir_path is not None:
                    cmd_args['--certdir'] = voms_certdir_path

                if voms_vomsdir_path is not None:
                    cmd_args['--vomsdir'] = voms_vomsdir_path

                if voms_vomses_path is not None:
                    cmd_args['--vomses'] = voms_vomses_path
        else:
            executable = "grid-proxy-init"

        try:
            args = []
            for option in cmd_args:
                args.append(option)
                args.append(cmd_args[option])

            process = subprocess.Popen([executable] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()

            if process.returncode != 0:
                download_logger.error("Generating proxy certificate fails, process returns non-zero code.")
                download_logger.error(out)
                download_logger.error(err)
                return None

            return dest_proxy_path
        except subprocess.SubprocessError:
            traceback.print_exc()
            return None

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
