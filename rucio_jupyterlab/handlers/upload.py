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


class UploadValidationError(ValueError):
    """Raised when an upload request contains invalid parameters."""


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


class UploadHandler(RucioAPIHandler):
    @staticmethod
    def _parse_upload_request(json_body):
        if not isinstance(json_body, dict):
            raise UploadValidationError("Invalid POST body.")

        file_paths = json_body.get('file_paths')
        if (not isinstance(file_paths, list) or not file_paths or
                any(not _is_non_empty_string(file_path) for file_path in file_paths)):
            raise UploadValidationError("Missing or invalid 'file_paths'.")

        rse = json_body.get('rse')
        scope = json_body.get('scope')
        if not _is_non_empty_string(rse) or not _is_non_empty_string(scope):
            raise UploadValidationError("Missing 'rse' or 'scope'.")
        rse = rse.strip()
        scope = scope.strip()

        add_to_dataset = json_body.get('add_to_dataset', False)
        if not isinstance(add_to_dataset, bool):
            raise UploadValidationError("Invalid 'add_to_dataset'.")

        lifetime = json_body.get('lifetime')
        if lifetime == '':
            lifetime = None
        if not add_to_dataset:
            dataset_scope = None
            dataset_name = None
            if (lifetime is not None and
                    (isinstance(lifetime, bool) or not isinstance(lifetime, int) or lifetime < 0)):
                raise UploadValidationError("Invalid 'lifetime'.")
        else:
            dataset_scope = json_body.get('dataset_scope')
            dataset_name = json_body.get('dataset_name')
            if not _is_non_empty_string(dataset_scope) or not _is_non_empty_string(dataset_name):
                raise UploadValidationError("Dataset scope and name are required.")
            if lifetime is not None:
                raise UploadValidationError("Lifetime is not supported for dataset uploads.")
            dataset_scope = dataset_scope.strip()
            dataset_name = dataset_name.strip()

        return file_paths, rse, scope, dataset_scope, dataset_name, lifetime

    @tornado.web.authenticated
    @prometheus_metrics
    def post(self):
        try:
            namespace = self.get_query_argument('namespace')
            json_body = self.get_json_body()
            try:
                file_paths, rse, scope, dataset_scope, dataset_name, lifetime = self._parse_upload_request(json_body)
            except UploadValidationError as e:
                logger.warning("Invalid upload request: %s", e)
                self.set_status(400)
                self.finish({'success': False, 'error': str(e)})
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
        args = (namespace, rucio, file_paths, rse, scope, dataset_scope, dataset_name, lifetime)
        logger.info("Spawning upload process for %d files to RSE '%s' in scope '%s'.", len(file_paths), rse, scope)
        process = mp.Process(target=RucioFileUploader.start_upload_batch_target, args=args)
        process.start()
        logger.debug("Started process %s for upload batch.", process.pid)
