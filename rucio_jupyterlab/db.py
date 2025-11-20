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
import json
from peewee import SqliteDatabase, Model, TextField, IntegerField, DateTimeField, CompositeKey, BooleanField
from .entity import AttachedFile


def prepare_db(dir_path):
    path = os.path.join(dir_path, 'cache.db')
    return SqliteDatabase(path)


def prepare_directory(dir_path):
    os.makedirs(dir_path, exist_ok=True)


# Check if we're in a Kubernetes environment and use local storage
# to avoid slow NFS/EFS performance with SQLite
if os.getenv('JUPYTERHUB_SERVICE_PREFIX') or os.getenv('KUBERNETES_SERVICE_HOST'):
    # In K8s, use local ephemeral storage instead of home dir (which is often NFS)
    dir_path = os.getenv('RUCIO_CACHE_DIR', '/tmp/.rucio_jupyterlab')
    import logging
    logging.getLogger(__name__).info(f"Kubernetes environment detected. Using local cache directory: {dir_path}")
else:
    dir_path = os.path.expanduser("~/.rucio_jupyterlab")

prepare_directory(dir_path)
db = prepare_db(dir_path)


def get_db():
    db.create_tables([UserConfig, RucioAuthCredentials, AttachedFilesListCache, FileReplicasCache, FileUploadJob])
    return DatabaseInstance()


class DatabaseInstance:
    def put_config(self, key, value):
        UserConfig.replace(key=key, value=value).execute()

    def get_config(self, key):
        config = UserConfig.get_or_none(UserConfig.key == key)
        if config:
            return config.value

        return None

    def get_active_instance(self):
        return self.get_config('instance')

    def set_active_instance(self, instance_name):
        self.put_config('instance', instance_name)

    def get_active_auth_method(self):
        return self.get_config('auth_method')

    def set_active_auth_method(self, auth_method):
        self.put_config('auth_method', auth_method)

    def get_rucio_auth_credentials(self, namespace, auth_type):
        creds = RucioAuthCredentials.get_or_none(namespace=namespace, auth_type=auth_type)
        if creds:
            return json.loads(creds.params)

        return None

    def set_rucio_auth_credentials(self, namespace, auth_type, params):
        params_str = json.dumps(params)
        RucioAuthCredentials.replace(namespace=namespace, auth_type=auth_type, params=params_str).execute()

    def get_attached_files(self, namespace, did):
        current_time = int(time.time())
        db_attached_files = AttachedFilesListCache.get_or_none(
            (AttachedFilesListCache.namespace == namespace) & (AttachedFilesListCache.did == did) & (AttachedFilesListCache.expiry > current_time))
        if db_attached_files:
            json_attached_files = json.loads(db_attached_files.file_dids)

            attached_files = []
            for json_attached_file in json_attached_files:
                attached_file = AttachedFile(did=json_attached_file.get('did'), size=json_attached_file.get('size'))
                attached_files.append(attached_file)

            return attached_files

        return None

    def set_attached_files(self, namespace, parent_did, attached_files):
        cache_expires = int(time.time()) + (3600)  # an hour TODO change?
        attached_files_dict = [x.__dict__ for x in attached_files]
        file_dids_json = json.dumps(attached_files_dict)
        AttachedFilesListCache.replace(namespace=namespace, did=parent_did,
                                       file_dids=file_dids_json, expiry=cache_expires).execute()

    def get_file_replica(self, namespace, file_did):
        current_time = int(time.time())
        replica_cache = FileReplicasCache.get_or_none((FileReplicasCache.namespace == namespace) & (
            FileReplicasCache.did == file_did) & (FileReplicasCache.expiry > current_time))

        return replica_cache

    def get_file_replicas_bulk(self, namespace, file_dids):
        """
        Retrieve multiple file replicas in a single query to avoid N+1 problem.

        Args:
            namespace (str): Cache namespace.
            file_dids (list): List of DIDs to fetch.

        Returns:
            dict: Mapping of DID to replica object, or empty dict if any are missing/expired.
        """
        if not file_dids:
            return {}

        current_time = int(time.time())
        
        # Fetch all replicas in one query
        replicas = (FileReplicasCache
                   .select()
                   .where(
                       (FileReplicasCache.namespace == namespace) &
                       (FileReplicasCache.did.in_(file_dids)) &
                       (FileReplicasCache.expiry > current_time)
                   ))
        
        # Build a dict for O(1) lookups
        replica_dict = {r.did: r for r in replicas}
        
        # Check if we got all of them
        if len(replica_dict) != len(file_dids):
            # Some are missing or expired - return None to indicate incomplete cache
            return None
        
        return replica_dict

    def set_file_replica(self, namespace, file_did, pfn, size):
        cache_expires = int(time.time()) + (3600)  # an hour TODO change?
        FileReplicasCache.replace(
            namespace=namespace, did=file_did, pfn=pfn, size=size, expiry=cache_expires).execute()

    def set_file_replicas_bulk(self, namespace, file_replicas, chunk_size=1000):
        """
        Store many file replicas in a single transaction to avoid per-row commits.

        Args:
            namespace (str): Cache namespace.
            file_replicas (Iterable): Collection of objects exposing did, pfn, size.
            chunk_size (int): Number of rows per bulk insert to keep memory bounded.
        """
        if not file_replicas:
            return

        cache_expires = int(time.time()) + (3600)  # an hour TODO change?

        def iter_rows():
            for replica in file_replicas:
                yield {
                    'namespace': namespace,
                    'did': replica.did,
                    'pfn': replica.pfn,
                    'size': replica.size,
                    'expiry': cache_expires
                }

        with db.atomic():
            rows_buffer = []
            for row in iter_rows():
                rows_buffer.append(row)
                if len(rows_buffer) >= chunk_size:
                    (FileReplicasCache
                     .insert_many(rows_buffer)
                     .on_conflict_replace()
                     .execute())
                    rows_buffer.clear()

            if rows_buffer:
                (FileReplicasCache
                 .insert_many(rows_buffer)
                 .on_conflict_replace()
                 .execute())

    def get_upload_jobs(self, namespace):
        upload_jobs = FileUploadJob.select().dicts().where(FileUploadJob.namespace == namespace).execute()
        return upload_jobs

    def get_upload_job(self, job_id):
        upload_jobs = FileUploadJob.select().dicts().where(FileUploadJob.id == job_id).execute()
        return upload_jobs[0]

    def add_upload_job(self, namespace, did, dataset_did, path, rse, lifetime, pid):
        return FileUploadJob.insert(namespace=namespace, did=did, dataset_did=dataset_did, path=path, rse=rse, lifetime=lifetime, pid=pid, uploaded=False).execute()

    def delete_upload_job(self, id):
        job = FileUploadJob.get_or_none(id)
        if job is not None:
            job.delete_instance()

    def mark_upload_job_finished(self, id):
        job = FileUploadJob.get_or_none(id)
        if job is not None:
            job.uploaded = True
            job.save()

        return job

    def purge_cache(self):
        FileReplicasCache.delete().execute(database=None)
        AttachedFilesListCache.delete().execute(database=None)
        FileUploadJob.delete().execute(database=None)


class UserConfig(Model):
    key = TextField(unique=True)
    value = TextField()

    class Meta:
        database = db


class RucioAuthCredentials(Model):
    namespace = TextField()
    auth_type = TextField()
    params = TextField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey('namespace', 'auth_type')


class AttachedFilesListCache(Model):
    namespace = TextField()
    did = TextField()
    file_dids = TextField()
    expiry = DateTimeField()

    class Meta:
        database = db
        primary_key = CompositeKey('namespace', 'did')


class FileReplicasCache(Model):
    namespace = TextField()
    did = TextField()
    pfn = TextField(null=True)
    size = IntegerField()
    expiry = DateTimeField()

    class Meta:
        database = db
        primary_key = CompositeKey('namespace', 'did')


class FileUploadJob(Model):
    id = IntegerField(primary_key=True)
    namespace = TextField()
    did = TextField()
    dataset_did = TextField(null=True)
    path = TextField()
    rse = TextField()
    uploaded = BooleanField()
    lifetime = IntegerField(null=True)
    pid = IntegerField()

    class Meta:
        database = db
        # primary_key = CompositeKey('namespace', 'did')
