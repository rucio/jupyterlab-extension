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
import multiprocessing as mp
import logging
import json
from logging.handlers import QueueHandler, QueueListener
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile
import rucio_jupyterlab.utils as utils
from rucio_jupyterlab.rucio.download import RucioFileDownloader
from rucio_jupyterlab.rucio.exceptions import RucioAPIException

logger = logging.getLogger(__name__)

BASE_DIR = '~/rucio/downloads'


class DownloadModeHandler:
    STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
    STATUS_REPLICATING = "REPLICATING"
    STATUS_OK = "OK"
    STATUS_STUCK = "STUCK"
    STATUS_FAILED = "FAILED"

    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name

    def background_worker(self, log_queue, did):

        # Attach a QueueHandler so logs go to the main process
        queue_handler = QueueHandler(log_queue)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.handlers = []  # Clear any inherited handlers
        logger.addHandler(queue_handler)

        # Now logging works as usual, but goes to the main process
        logger.info("Starting download for DID '%s'", did)

        # Your actual download logic here
        try:
            RucioFileDownloader.start_download_target(self.namespace, did, self.rucio)
        except Exception as e:
            logger.exception("Error downloading %s: %s", did, e)

    def make_available(self, scope, name):
        """
        Triggers a download process for a given DID, with error handling.
        """

        # Create a multiprocessing-safe log queue
        log_queue = mp.Queue()

        # Set up the handlers that the main process will use (e.g. console)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(processName)s - %(levelname)s - %(message)s'))

        # Set up the queue listener in the main process
        queue_listener = QueueListener(log_queue, console_handler)
        queue_listener.start()

        did = f'{scope}:{name}'
        logger.info("Attempting to make DID '%s' available.", did)

        # Get the destination folder once to avoid repeated calls
        dest_folder = RucioFileDownloader.get_dest_folder(self.namespace, did)

        # --- This is the clean way to clear previous states ---
        # These functions internally handle if the file doesn't exist
        RucioFileDownloader.delete_errorfile(dest_folder)
        RucioFileDownloader.delete_donefile(dest_folder)  # Important: Clear previous success state too
        RucioFileDownloader.delete_lockfile(dest_folder)  # Important: Clear any stale lock files

        try:
            paths = self._get_file_paths(did)
            if paths:
                # Check if all files are already present and valid.
                if not utils.find(lambda x: not os.path.isfile(paths[x]), paths):
                    logger.info("All files for DID '%s' are already available. No action needed.", did)
                    return

            logger.info("Starting background download process for DID '%s'.", did)
            RucioFileDownloader.write_lockfile(dest_folder)
            # RucioFileDownloader.start_download_target(self.namespace, did, self.rucio)
            # process = mp.Process(target=RucioFileDownloader.start_download_target, args=(self.namespace, did, self.rucio))
            process = mp.Process(
                target=DownloadModeHandler.background_worker,
                args=(self, log_queue, did),
                name=f"DownloadProcess-{did}"  # Optional: Name the process for easier debugging
            )
            process.start()

        except RucioAPIException as e:
            # Handle specific Rucio API errors
            logger.error("Rucio API error while making DID '%s' available: %s", did, e)
            # Re-raise the exception to be handled by the caller (e.g., to return an HTTP 500)
            raise
        except Exception as e:
            # Handle any other unexpected errors
            logger.exception("An unexpected error occurred in make_available for DID '%s'", did)
            RucioFileDownloader.write_errorfile(dest_folder, e)
            RucioFileDownloader.delete_lockfile(dest_folder)
            raise

    def get_did_details(self, scope, name, force_fetch=False):
        """
        Retrieves the status of files for a DID, with error handling.
        """
        did = f'{scope}:{name}'
        logger.info("Fetching details for DID '%s' (force_fetch=%s).", did, force_fetch)

        try:
            attached_files = self._get_attached_files(scope, name, force_fetch)
            if not attached_files:
                logger.warning("No attached files found for DID '%s'.", did)
                return []

            dest_dir_exists = self._dest_dir_exists(did)
            is_downloading = self._is_downloading(did)
            paths = self._get_file_paths(did)
            error_details = self._get_error_details(did)

            def result_mapper(file, _):
                logger.debug("Mapping status for file '%s' in parent DID '%s'.", file.did, did)

                if error_details:
                    return {"status": self.STATUS_FAILED, "did": file.did, "path": None, "size": file.size, "error": error_details.get('exception_message', 'Unknown error')}

                if not dest_dir_exists:
                    return {"status": self.STATUS_NOT_AVAILABLE, "did": file.did, "path": None, "size": file.size}

                if is_downloading:
                    return {"status": self.STATUS_REPLICATING, "did": file.did, "path": None, "size": file.size}

                if not paths:
                    logger.warning("Paths not found for DID '%s'; file '%s' is STUCK.", did, file.did)
                    return {"status": self.STATUS_STUCK, "did": file.did, "path": None, "size": file.size}

                path = paths.get(file.did)
                if not path or not os.path.isfile(path):
                    logger.warning("File '%s' not found at expected path '%s'. Status: STUCK.", file.did, path)
                    return {"status": self.STATUS_STUCK, "did": file.did, "path": None, "size": file.size}

                return {"status": self.STATUS_OK, "did": file.did, "path": None, "size": file.size}

            results = utils.map(attached_files, result_mapper)
            logger.info("Successfully fetched details for %d files for DID '%s'.", len(results), did)
            return results

        except RucioAPIException as e:
            logger.error("Rucio API error while fetching details for DID '%s': %s", did, e)
            raise
        except Exception as e:
            logger.exception("An unexpected error occurred in get_did_details for DID '%s'", did)
            raise

    def _get_error_details(self, did):
        """
        Checks for and reads an error.json file.
        """
        dest_folder = RucioFileDownloader.get_dest_folder(self.namespace, did)
        error_file_path = os.path.join(dest_folder, 'error.json')
        if os.path.exists(error_file_path):
            try:
                with open(error_file_path, 'r') as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Could not read or parse error file at '{error_file_path}': {e}")
                return {'exception_message': 'Error file is corrupted or unreadable.'}
        return None

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
