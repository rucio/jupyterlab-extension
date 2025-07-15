# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import os
import time
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
    def write_errorfile(dest_folder, exception):
        """
        Writes exception details to an error.json file in the destination folder.
        """
        error_file_path = os.path.join(dest_folder, 'error.json')

        # Create a serializable payload from the exception
        error_payload = {
            'success': False,
            'error': 'DownloadFailed',
            'exception_class': exception.__class__.__name__,
            # Use getattr to safely access optional attributes on the exception
            'exception_message': str(exception)
        }

        logger.error("Writing error file to '%s' with details: %s", error_file_path, error_payload)
        with open(error_file_path, 'w') as f:
            json.dump(error_payload, f)

    def start_download_target(namespace, did, rucio):
        dest_folder = RucioFileDownloader.get_dest_folder(namespace, did)
        logger.info("Preparing to download DID '%s' to '%s'.", did, dest_folder)

        try:
            with RucioClientEnvironment(rucio) as rucio_home:
                os.makedirs(dest_folder, exist_ok=True)

                try:
                    results = RucioFileDownloader.download(dest_folder, did)
                    logger.info("Download successful for DID '%s'.", did)
                    RucioFileDownloader.write_donefile(dest_folder, results)
                    logger.info("Donefile written for '%s'.", dest_folder)

                except Exception as e:
                    # Log the exception and write the error file
                    logger.exception("Download failed for DID '%s': %s", did, e)
                    RucioFileDownloader.write_errorfile(dest_folder, e)

                finally:
                    # Always remove the lockfile when the operation is complete (or has failed)
                    RucioFileDownloader.delete_lockfile(dest_folder)
                    logger.debug("Lockfile deleted for '%s'.", dest_folder)

        except Exception as e:
            # Catch any other exception during setup (e.g., permissions)
            logger.error("A critical error occurred before download could start for DID '%s': %s", did, e)
            # Ensure the destination folder exists to write the error file
            os.makedirs(dest_folder, exist_ok=True)
            RucioFileDownloader.write_errorfile(dest_folder, e)
            RucioFileDownloader.delete_lockfile(dest_folder)

    @staticmethod
    def is_downloading(dest_path):
        lockfile_path = os.path.join(dest_path, '.lockfile')
        if not os.path.isfile(lockfile_path):
            logger.debug("No lockfile found at '%s'.", lockfile_path)
            return False

        try:
            with open(lockfile_path, 'r') as lockfile:
                pid_str = lockfile.read().strip()
                if not pid_str.isdigit():
                    logger.warning("Invalid PID in lockfile '%s': '%s'", lockfile_path, pid_str)
                    return False
                pid = int(pid_str)
                if not psutil.pid_exists(pid):
                    logger.debug("Process with PID %s from lockfile does not exist.", pid)
                    return False
                process = psutil.Process(pid=pid)
                is_active = process.is_running() and process.status() != psutil.STATUS_ZOMBIE
                logger.debug("Lockfile PID %s is_active=%s.", pid, is_active)
                return is_active
        except Exception as e:
            logger.warning("Error reading or validating lockfile '%s': %s", lockfile_path, e)
            return False

    @staticmethod
    def download(dest_path, did):
        from rucio.client import Client
        from rucio.client.downloadclient import DownloadClient

        client = Client()
        download_client = DownloadClient(client=client, logger=rucio_logger)

        try:
            logger.info("Starting download for DID '%s' into '%s'.", did, dest_path)
            results = download_client.download_dids([{'did': did, 'base_dir': dest_path}])
            logger.info("Download completed for DID '%s'.", did)
            return results
        except Exception as e:
            logger.exception("Exception during download for DID '%s': %s", did, e)
            raise

    @staticmethod
    def get_dest_folder(namespace, did):
        try:
            did_folder_name = str(base64.b32encode(did.encode('utf-8')), 'utf-8').lower().replace('=', '')
            dest_path = os.path.expanduser(os.path.join('~', 'rucio', namespace, 'downloads', did_folder_name))
            logger.debug("Destination folder for DID '%s' is '%s'.", did, dest_path)
            return dest_path
        except Exception as e:
            logger.error("Failed to compute destination folder for DID '%s': %s", did, e)
            raise

    @staticmethod
    def write_lockfile(dest_path):
        """
        Atomically creates a lockfile. Returns True on success, False if lock exists.
        """
        lockfile_path = os.path.join(dest_path, '.lockfile')
        try:
            # os.O_CREAT | os.O_EXCL is the key. It's an atomic "create if not exists" operation.
            # It will raise FileExistsError if the lockfile already exists.
            fd = os.open(lockfile_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, 'w') as f:
                f.write(str(os.getpid()))
            logger.info("Successfully acquired lock for '%s'.", dest_path)
            return True
        except FileExistsError:
            logger.warning("Lockfile already exists at '%s'. Another process is active.", lockfile_path)
            # Optional: Add logic here to check if the lock is stale (e.g., older than 24 hours)
            return False
        except Exception as e:
            logger.error("Failed to create lockfile at '%s': %s", lockfile_path, e)
            return False

    @staticmethod
    def delete_lockfile(dest_folder):
        file_path = os.path.join(dest_folder, '.lockfile')
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug("Lockfile '%s' deleted.", file_path)
            else:
                logger.debug("No lockfile to delete at '%s'.", file_path)
        except Exception as e:
            logger.warning("Failed to delete lockfile at '%s': %s", file_path, e)

    @staticmethod
    def delete_errorfile(dest_folder):
        """
        Deletes the error.json file in the specified destination folder if it exists.
        Logs the action or any errors encountered.
        """
        file_path = os.path.join(dest_folder, 'error.json')
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug("Error file '%s' deleted.", file_path)
            else:
                logger.debug("No error file to delete at '%s'.", file_path)
        except Exception as e:
            logger.warning("Failed to delete error file at '%s': %s", file_path, e)

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
                    logger.warning("No destination file path for DID '%s' in results.", did)

            content = json.dumps({'paths': paths})

            with open(file_path, 'w') as donefile:
                donefile.write(content)
            logger.debug("Donefile written at '%s'.", file_path)
        except Exception as e:
            logger.error("Failed to write donefile at '%s': %s", file_path, e)
            raise

    @staticmethod
    def delete_donefile(dest_folder):
        """
        Deletes the .donefile in the specified destination folder if it exists.
        Logs the action or any errors encountered.
        """
        file_path = os.path.join(dest_folder, '.donefile')
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug("Donefile '%s' deleted.", file_path)
            else:
                logger.debug("No donefile to delete at '%s'.", file_path)
        except Exception as e:
            logger.warning("Failed to delete donefile at '%s': %s", file_path, e)
