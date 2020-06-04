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
        config = UserConfig.get_or_none(UserConfig.key == key)
        if config:
            return config.value

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
        did_cache = DIDBrowserCache.get_or_none(
            DIDBrowserCache.namespace == self.namespace & DIDBrowserCache.did == parent_did)
        if did_cache:
            return json.loads(did_cache.file_dids)

        return None

    def set_cached_file_dids(self, parent_did, file_dids):
        cache_expires = int(time.time()) + (3600)  # an hour TODO change?
        file_dids_json = json.dumps(file_dids)
        DIDBrowserCache.replace(namespace=self.namespace, did=parent_did,
                                file_dids=file_dids_json, expiry=cache_expires).execute()

    def get_cached_file_details(self, file_did):
        current_time = int(time.time())
        return FileCache.get_or_none((FileCache.namespace == self.namespace) & (FileCache.did == file_did) & (FileCache.expiry > current_time))

    def set_cached_file_details(self, file_did, replication_status=None, replication_rule_id=None, path=None, expiry=None):
        cache = FileCache.get_or_none(namespace=self.namespace, did=file_did)

        if not expiry:
            expiry = int(time.time()) + (3600)  # TODO cache for an hour?

        if not cache:
            FileCache.create(namespace=self.namespace, did=file_did, replication_rule_id=replication_rule_id,
                             replication_status=replication_status, path=path, expiry=expiry)
        else:
            if replication_status:
                cache.replication_status = replication_status
            if replication_rule_id:
                cache.replication_rule_id = replication_rule_id
            if path:
                cache.path = path

            cache.expiry = expiry
            cache.save()


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
    replication_rule_id = TextField(null=True)
    replication_status = TextField()
    path = TextField(null=True)
    expiry = DateTimeField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey('namespace', 'did')
