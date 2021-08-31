# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021

import tornado
from rucio_jupyterlab.rucio.upload import RucioFileUploader
from .base import RucioAPIHandler


class UploadJobsDetailsHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        job_id = self.get_query_argument('id')
        rucio_instance = self.rucio.for_instance(namespace)
        uploader = RucioFileUploader(namespace=namespace, rucio=rucio_instance)

        upload_job = uploader.get_upload_job(job_id=job_id)
        self.finish(upload_job)

    @tornado.web.authenticated
    def delete(self):
        namespace = self.get_query_argument('namespace')
        job_id = self.get_query_argument('id')
        rucio_instance = self.rucio.for_instance(namespace)
        uploader = RucioFileUploader(namespace=namespace, rucio=rucio_instance)

        uploader.delete_upload_job(job_id=job_id)
        self.finish({'success': True})
