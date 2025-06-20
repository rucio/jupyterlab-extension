# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import logging
import multiprocessing as mp
from rucio_jupyterlab.rucio.upload import RucioFileUploader
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics
from rucio_jupyterlab.rucio.exceptions import RucioAPIException
import tornado

logger = logging.getLogger(__name__)


class UploadHandler(RucioAPIHandler):
    @tornado.web.authenticated
    @prometheus_metrics
    def post(self):
        try:
            namespace = self.get_query_argument('namespace')
            json_body = self.get_json_body()
            file_paths = json_body.get('file_paths')
            rse = json_body.get('rse')
            scope = json_body.get('scope')
            add_to_dataset = json_body.get('add_to_dataset', False)
            dataset_name = json_body.get('dataset_name') if add_to_dataset else None
            dataset_scope = json_body.get('dataset_scope') if add_to_dataset else None
            lifetime = json_body.get('lifetime')

            # Validate required fields
            if not file_paths or not isinstance(file_paths, list):
                logger.warning("Missing or invalid 'file_paths' in POST body.")
                self.set_status(400)
                self.finish({'success': False, 'error': "Missing or invalid 'file_paths'."})
                return
            if not rse or not scope:
                logger.warning("Missing 'rse' or 'scope' in POST body.")
                self.set_status(400)
                self.finish({'success': False, 'error': "Missing 'rse' or 'scope'."})
                return

            try:
                rucio_instance = self.rucio.for_instance(namespace)
            except Exception as e:
                logger.error("Failed to get Rucio instance for namespace '%s': %s", namespace, e, exc_info=True)
                self.set_status(500)
                self.finish({'success': False, 'error': "Failed to get Rucio instance."})
                return

            logger.info("Starting upload for files %s to RSE '%s' in scope '%s' (namespace '%s').", file_paths, rse, scope, namespace)

            UploadHandlerImpl.upload(
                namespace=namespace,
                rucio=rucio_instance,
                file_paths=file_paths,
                rse=rse,
                scope=scope,
                dataset_scope=dataset_scope,
                dataset_name=dataset_name,
                lifetime=lifetime
            )

            self.finish({'success': True})

        except RucioAPIException as e:
            logger.error("Rucio API error during upload: %s", e, exc_info=True)
            self.set_status(502)
            self.finish({'success': False, 'error': f"Rucio error: {e}"})
        except Exception as e:
            logger.error("Unexpected error in UploadHandler: %s", e, exc_info=True)
            self.set_status(500)
            self.finish({'success': False, 'error': "Internal server error."})


class UploadHandlerImpl:
    @staticmethod
    def upload(namespace, rucio, file_paths, rse, scope, dataset_scope=None, dataset_name=None, lifetime=None):
        for file_path in file_paths:
            args = (namespace, rucio, file_path, rse, scope, dataset_scope, dataset_name, lifetime)
            try:
                logger.info("Spawning upload process for '%s' to RSE '%s' in scope '%s'.", file_path, rse, scope)
                process = mp.Process(target=RucioFileUploader.start_upload_target, args=args)
                process.start()
                logger.debug("Started process %s for file '%s'.", process.pid, file_path)
            except Exception as e:
                logger.error("Failed to start upload process for '%s': %s", file_path, e, exc_info=True)
