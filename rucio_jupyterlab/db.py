import os
import time
import json
from peewee import *


def prepare_db(dir_path):
    path = os.path.join(dir_path, 'cache.db')
    return SqliteDatabase(path)


def prepare_directory(dir_path):
    os.makedirs(dir_path, exist_ok=True)


dir_path = os.path.expanduser("~/.rucio_jupyterlab")
prepare_directory(dir_path)
db = prepare_db(dir_path)


def get_db():
    db.create_tables([UserConfig, Bookmark, DIDBrowserCache, FileCache])
    return DatabaseInstance()


def get_namespaced_db(namespace):
    db.create_tables([UserConfig, Bookmark, DIDBrowserCache, FileCache])
    return NamespacedDatabaseInstance(namespace)


class DatabaseInstance:
    def put_config(self, key, value):
        UserConfig.replace(key=key, value=value).execute()

    def get_config(self, key):
        try:
            return UserConfig.get(UserConfig.key == key).value
        except DoesNotExist:
            return None

    def get_active_instance(self):
        return self.get_config('instance')

    def set_active_instance(self, instance_name):
        self.put_config('instance', instance_name)


class NamespacedDatabaseInstance(DatabaseInstance):
    def __init__(self, namespace):
        self.namespace = namespace

    def get_bookmark(self):
        return Bookmark.select().where(Bookmark.namespace == self.namespace)

    def insert_bookmark(self, did, did_type):
        Bookmark.create(namespace=self.namespace, did=did, did_type=did_type)

    def delete_bookmark(self, did):
        bookmark = Bookmark.get(Bookmark.namespace ==
                                self.namespace, Bookmark.did == did)
        bookmark.delete_instance()

    def get_cached_file_dids(self, parent_did):
        try:
            did_cache = DIDBrowserCache.get(DIDBrowserCache.namespace == self.namespace and DIDBrowserCache.did == parent_did)
            return json.loads(did_cache.file_dids)
        except DoesNotExist:
            return None
        
    def set_cached_file_dids(self, parent_did, file_dids):
        cache_expires = int(time.time()) + (3600)  # an hour TODO change?
        file_dids_json = json.dumps(file_dids)
        DIDBrowserCache.replace(namespace=self.namespace, did=parent_did, file_dids=file_dids_json, expiry=cache_expires).execute()


class UserConfig(Model):
    key = TextField(unique=True)
    value = TextField()

    class Meta:
        database = db


class Bookmark(Model):
    namespace = TextField()
    did = TextField()
    did_type = IntegerField()

    class Meta:
        database = db
        primary_key = CompositeKey('namespace', 'did')


class DIDBrowserCache(Model):
    namespace = TextField()
    did = TextField()
    file_dids = TextField()
    expiry = DateTimeField()

    class Meta:
        database = db
        primary_key = CompositeKey('namespace', 'did')


class FileCache(Model):
    namespace = TextField()
    did = TextField()
    rse = TextField()
    replication_rule_id = TextField()
    replication_status = IntegerField()
    path = TextField()
    expiry = DateTimeField()

    class Meta:
        database = db
        primary_key = CompositeKey('namespace', 'did')
