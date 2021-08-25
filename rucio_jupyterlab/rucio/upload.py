# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021

import os
import psutil
import logging
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.rucio.client_environment import RucioClientEnvironment

upload_logger = logging.getLogger('UploadLogger')
upload_logger.setLevel(logging.DEBUG)


class RucioFileUploader:
    STATUS_UPLOADING = "UPLOADING"
    STATUS_OK = "OK"
    STATUS_FAILED = "FAILED"

    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name

    @staticmethod
    def start_upload_target(namespace, rucio, file_paths, rse, scope, dataset_name=None, lifetime=None):
        with RucioClientEnvironment(rucio) as rucio_home:
            uploader = RucioFileUploader(namespace, rucio)
            uploader.upload(scope, file_paths, rse, lifetime)

    def get_upload_jobs(self):
        upload_jobs = self.db.get_upload_jobs(self.namespace)
        output = []
        for upload_job in upload_jobs:
            output.append({
                **upload_job,
                'status': self._get_job_status(pid=upload_job.pid, uploaded=upload_job.uploaded)
            })
        return output

    def _get_job_status(self, pid, uploaded):
        if uploaded:
            return STATUS_OK

        pid_exists = psutil.pid_exists(pid)
        if pid_exists:
            process = psutil.Process(pid=pid)
            if process.is_running() and process.status() != 'zombie':
                return STATUS_UPLOADING

        return STATUS_FAILED

    def upload(self, file_paths, rse, scope, dataset_name=None, lifetime=None):
        from rucio.client import Client
        from rucio.client.uploadclient import UploadClient

        client = Client()
        upload_client = UploadClient(client=client, logger=upload_logger)

        upload_job_ids = self.add_upload_jobs(file_paths, rse, scope)

        items = []
        for path in file_paths:
            items.append({
                'path': path,
                'rse': rse,
                'did_scope': scope,
                'dataset_scope': scope if dataset_name else None,
                'dataset_name': dataset_name,
                'lifetime': lifetime
            })

        status = upload_client.upload(items=items)
        if status == 0:
            upload_logger.debug("Upload successful")
            self.mark_upload_jobs_finished(upload_job_ids)
        else:
            upload_logger.error("Upload failed, status: %s", status)

    def add_upload_jobs(self, file_paths, rse, scope):
        job_ids = []
        for path in file_paths:
            file_name = path.strip('/').split('/')[-1]
            did = scope + ':' + file_name
            upload_job = self.db.add_upload_job(namespace=namespace, did=did, rse=rse, pid=os.getpid())
            job_ids.append(upload_job.id)

        return job_ids

    def mark_upload_jobs_finished(self, upload_job_ids):
        for job_id in upload_job_ids:
            self.db.mark_upload_job_finished(job_id)
