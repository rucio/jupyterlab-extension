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


class UploadJobsLogHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        job_id = self.get_query_argument('id')
        rucio_instance = self.rucio.for_instance(namespace)
        uploader = RucioFileUploader(namespace=namespace, rucio=rucio_instance)

        try:
            log_text = uploader.get_upload_job_log(job_id=job_id)
        except FileNotFoundError:
            log_text = "Logfile does not exist"
            self.set_status(404)

        self.finish({'text': log_text})
