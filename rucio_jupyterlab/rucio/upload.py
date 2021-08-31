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

LOGFILE_DIR = os.path.expanduser('~/.rucio_jupyterlab/logs/upload')


class RucioFileUploader:
    STATUS_UPLOADING = "UPLOADING"
    STATUS_OK = "OK"
    STATUS_FAILED = "FAILED"

    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name

    @staticmethod
    def start_upload_target(namespace, rucio, file_path, rse, scope, dataset_scope=None, dataset_name=None, lifetime=None):
        with RucioClientEnvironment(rucio) as rucio_home:
            uploader = RucioFileUploader(namespace, rucio)
            uploader.upload(file_path=file_path, rse=rse, scope=scope, dataset_scope=dataset_scope, dataset_name=dataset_name, lifetime=lifetime)

    def get_upload_jobs(self):
        upload_jobs = self.db.get_upload_jobs(self.namespace)
        output = []
        for upload_job in upload_jobs:
            output.append({
                **upload_job,
                'status': self._get_job_status(pid=upload_job['pid'], uploaded=upload_job['uploaded'])
            })
        return output

    def get_upload_job(self, job_id):
        upload_job = self.db.get_upload_job(job_id)
        return {
            **upload_job,
            'status': self._get_job_status(pid=upload_job['pid'], uploaded=upload_job['uploaded'])
        }

    def get_upload_job_log(self, job_id):
        logfile_path = os.path.join(LOGFILE_DIR, f"{job_id}.log")
        with open(logfile_path, 'r') as f:
            return f.read()

    def delete_upload_job(self, job_id):
        self.db.delete_upload_job(job_id)
        try:
            logfile_path = os.path.join(LOGFILE_DIR, f"{job_id}.log")
            os.remove(logfile_path)
        except OSError:
            pass

    def _get_job_status(self, pid, uploaded):
        if uploaded:
            return RucioFileUploader.STATUS_OK

        pid_exists = psutil.pid_exists(pid)
        if pid_exists:
            process = psutil.Process(pid=pid)
            if process.is_running() and process.status() != 'zombie':
                return RucioFileUploader.STATUS_UPLOADING

        return RucioFileUploader.STATUS_FAILED

    def upload(self, file_path, rse, scope, dataset_scope=None, dataset_name=None, lifetime=None):
        from rucio.client.uploadclient import UploadClient

        upload_job_id = self.add_upload_job(
            path=file_path,
            rse=rse,
            scope=scope,
            lifetime=lifetime,
            dataset_scope=dataset_scope,
            dataset_name=dataset_name
        )

        os.makedirs(LOGFILE_DIR, exist_ok=True)
        logfile_path = os.path.join(LOGFILE_DIR, f"{upload_job_id}.log")

        upload_logger = logging.getLogger('UploadLogger')
        upload_logger.setLevel(logging.DEBUG)
        upload_logger.addHandler(logging.FileHandler(logfile_path))
        upload_logger.addHandler(logging.StreamHandler())

        item = {
            'path': os.path.abspath(file_path),
            'rse': rse,
            'did_scope': scope,
            'dataset_scope': dataset_scope,
            'dataset_name': dataset_name,
            'lifetime': lifetime
        }

        try:
            upload_client = UploadClient(logger=upload_logger)
            status = upload_client.upload(items=[item])
            if status == 0:
                self.db.mark_upload_job_finished(upload_job_id)
                os.remove(logfile_path)
        except:
            upload_logger.exception("Upload failed")

    def add_upload_job(self, path, rse, scope, lifetime=None, dataset_scope=None, dataset_name=None):
        file_name = path.strip('/').split('/')[-1]
        did = scope + ':' + file_name
        dataset_did = None
        if dataset_scope and dataset_scope:
            dataset_did = dataset_scope + ':' + dataset_name

        upload_job_id = self.db.add_upload_job(
            namespace=self.namespace,
            did=did,
            dataset_did=dataset_did,
            path=path,
            rse=rse,
            lifetime=lifetime,
            pid=os.getpid()
        )
        return upload_job_id
