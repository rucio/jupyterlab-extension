# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from rucio_jupyterlab.entity import AttachedFile


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class MockDatabaseInstance:
    def put_config(self, key, value):
        pass

    def get_config(self, key):
        return Struct(key=key, value='value')

    def get_active_instance(self):
        return 'atlas'

    def set_active_instance(self, instance_name):
        pass

    def get_active_auth_method(self):
        return 'userpass'

    def set_active_auth_method(self, auth_method):
        pass

    def get_rucio_auth_credentials(self, namespace, auth_type):
        pass

    def set_rucio_auth_credentials(self, namespace, auth_type, params):
        pass

    def get_attached_files(self, namespace, did):
        return [
            AttachedFile(did='scope:name1', size=123456),
            AttachedFile(did='scope:name2', size=123456),
            AttachedFile(did='scope:name3', size=123456)
        ]

    def set_attached_files(self, namespace, parent_did, attached_files):
        pass

    def get_file_replica(self, namespace, file_did):
        current_time = 168999754
        return Struct(namespace='atlas', did='scope:name', pfn='root://root//home/abcde', size=123456, expiry=current_time + 3600)

    def get_file_replicas_bulk(self, namespace, file_dids):
        """Mock bulk replica retrieval - returns dict of all requested DIDs."""
        current_time = 168999754
        replica_dict = {}
        for file_did in file_dids:
            replica_dict[file_did] = Struct(
                namespace=namespace, 
                did=file_did, 
                pfn='root://root//home/abcde', 
                size=123456, 
                expiry=current_time + 3600
            )
        return replica_dict

    def set_file_replica(self, namespace, file_did, pfn, size):
        pass

    def set_file_replicas_bulk(self, namespace, file_replicas, chunk_size=1000):  # pylint: disable=unused-argument
        pass
