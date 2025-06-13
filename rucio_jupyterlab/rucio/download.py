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

logger = logging.getLogger(__name__)

def rucio_logger(level, msg, *args, **kwargs):
    # Try to detect if only a message is passed
    if isinstance(level, str):
        msg = level
        level = logging.INFO
    logger = logging.getLogger("rucio.client.downloadclient")
    logger.log(level, msg, *args, **kwargs)

class RucioFileDownloader:
    @staticmethod
    def start_download_target(namespace, did, rucio):
        dest_folder = RucioFileDownloader.get_dest_folder(namespace, did)
        logger.info(f"Preparing to download DID '{did}' to '{dest_folder}'.")

        if RucioFileDownloader.is_downloading(dest_folder):
            logger.warning(f"Download already in progress for DID '{did}' in '{dest_folder}'. Skipping new download request.")
            return

        try:
            with RucioClientEnvironment(rucio) as rucio_home:
                logger.debug(f"Rucio environment prepared at '{rucio_home}'.")
                os.makedirs(dest_folder, exist_ok=True)
                logger.debug(f"Ensured destination folder exists: '{dest_folder}'.")
                RucioFileDownloader.write_lockfile(dest_folder)
                logger.info(f"Lockfile written for '{dest_folder}'.")

                try:
                    results = RucioFileDownloader.download(dest_folder, did)
                    logger.info(f"Download results for DID '{did}': {results}")
                    RucioFileDownloader.write_donefile(dest_folder, results)
                    logger.info(f"Donefile written for '{dest_folder}'.")
                except Exception as e:
                    logger.exception(f"Download failed for DID '{did}' in '{dest_folder}': {e}")
                    raise
                finally:
                    RucioFileDownloader.delete_lockfile(dest_folder)
                    logger.debug(f"Lockfile deleted for '{dest_folder}'.")
        except Exception as e:
            logger.error(f"Failed to start download for DID '{did}' in '{dest_folder}': {e}")

    @staticmethod
    def is_downloading(dest_path):
        lockfile_path = os.path.join(dest_path, '.lockfile')
        if not os.path.isfile(lockfile_path):
            logger.debug(f"No lockfile found at '{lockfile_path}'.")
            return False

        try:
            with open(lockfile_path, 'r') as lockfile:
                pid_str = lockfile.read().strip()
                if not pid_str.isdigit():
                    logger.warning(f"Invalid PID in lockfile '{lockfile_path}': '{pid_str}'")
                    return False
                pid = int(pid_str)
                if not psutil.pid_exists(pid):
                    logger.debug(f"Process with PID {pid} from lockfile does not exist.")
                    return False
                process = psutil.Process(pid=pid)
                is_active = process.is_running() and process.status() != psutil.STATUS_ZOMBIE
                logger.debug(f"Lockfile PID {pid} is_active={is_active}.")
                return is_active
        except Exception as e:
            logger.warning(f"Error reading or validating lockfile '{lockfile_path}': {e}")
            return False

    @staticmethod
    def download(dest_path, did):
        from rucio.client import Client
        from rucio.client.downloadclient import DownloadClient

        client = Client()
        download_client = DownloadClient(client=client, logger=rucio_logger)

        try:
            logger.info(f"Starting download for DID '{did}' into '{dest_path}'.")
            results = download_client.download_dids([{'did': did, 'base_dir': dest_path}])
            logger.info(f"Download completed for DID '{did}'.")
            return results
        except Exception as e:
            logger.exception(f"Exception during download for DID '{did}': {e}")
            raise

    @staticmethod
    def get_dest_folder(namespace, did):
        try:
            did_folder_name = str(base64.b32encode(did.encode('utf-8')), 'utf-8').lower().replace('=', '')
            dest_path = os.path.expanduser(os.path.join('~', 'rucio', namespace, 'downloads', did_folder_name))
            logger.debug(f"Destination folder for DID '{did}' is '{dest_path}'.")
            return dest_path
        except Exception as e:
            logger.error(f"Failed to compute destination folder for DID '{did}': {e}")
            raise

    @staticmethod
    def write_lockfile(dest_folder):
        file_path = os.path.join(dest_folder, '.lockfile')
        try:
            with open(file_path, 'w') as lockfile:
                content = str(os.getpid())
                lockfile.write(content)
            logger.debug(f"Lockfile written at '{file_path}' with PID {os.getpid()}.")
        except Exception as e:
            logger.error(f"Failed to write lockfile at '{file_path}': {e}")
            raise

    @staticmethod
    def delete_lockfile(dest_folder):
        file_path = os.path.join(dest_folder, '.lockfile')
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Lockfile '{file_path}' deleted.")
            else:
                logger.debug(f"No lockfile to delete at '{file_path}'.")
        except Exception as e:
            logger.warning(f"Failed to delete lockfile at '{file_path}': {e}")

    @staticmethod
    def write_donefile(dest_folder, results):
        file_path = os.path.join(dest_folder, '.donefile')
        paths = {}
        try:
            for result in results:
                scope = result.get('scope')
                name = result.get('name')
                did = f"{scope}:{name}"
                dest_file_paths = result.get('dest_file_paths', [])
                if dest_file_paths:
                    paths[did] = dest_file_paths[0]
                else:
                    logger.warning(f"No destination file path for DID '{did}' in results.")

            content = json.dumps({'paths': paths})

            with open(file_path, 'w') as donefile:
                donefile.write(content)
            logger.debug(f"Donefile written at '{file_path}'.")
        except Exception as e:
            logger.error(f"Failed to write donefile at '{file_path}': {e}")
            raise
