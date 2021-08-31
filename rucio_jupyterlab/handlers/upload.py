# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021

import tornado
import multiprocessing as mp
from rucio_jupyterlab.rucio.upload import RucioFileUploader
from .base import RucioAPIHandler


class UploadHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def post(self):
        namespace = self.get_query_argument('namespace')
        json_body = self.get_json_body()
        file_paths = json_body['file_paths']
        rse = json_body['rse']
        scope = json_body['scope']
        add_to_dataset = json_body.get('add_to_dataset', False)
        dataset_name = json_body.get('dataset_name') if add_to_dataset else None
        dataset_scope = json_body.get('dataset_scope') if add_to_dataset else None
        lifetime = json_body.get('lifetime')

        rucio_instance = self.rucio.for_instance(namespace)
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


class UploadHandlerImpl:
    @staticmethod
    def upload(namespace, rucio, file_paths, rse, scope, dataset_scope=None, dataset_name=None, lifetime=None):
        for file_path in file_paths:
            args = (namespace, rucio, file_path, rse, scope, dataset_scope, dataset_name, lifetime)
            process = mp.Process(target=RucioFileUploader.start_upload_target, args=args)
            process.start()
