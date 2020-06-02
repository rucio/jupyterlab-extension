import os
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
    db.create_tables([UserConfig, Bookmark, DatasetContainerCache, FileCache])
    return DatabaseInstance()


def get_namespaced_db(namespace):
    db.create_tables([UserConfig, Bookmark, DatasetContainerCache, FileCache])
    return NamespacedDatabaseInstance(namespace)


class DatabaseInstance:
    def put_config(self, key, value):
        UserConfig.replace(key=key, value=value).execute()

    def get_config(self, key):
        try:
            return UserConfig.get(UserConfig.key == key).value
        except DoesNotExist:
            return None


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


class BaseModel(Model):
    namespace = TextField()

    class Meta:
        database = db


class UserConfig(Model):
    key = TextField(unique=True)
    value = TextField()

    class Meta:
        database = db


class Bookmark(BaseModel):
    did = TextField(unique=True)
    did_type = IntegerField()


class DatasetContainerCache(BaseModel):
    did = TextField()
    file_did = TextField()
    expiry = DateTimeField()


class FileCache(BaseModel):
    did = TextField()
    rse = TextField()
    replication_rule_id = TextField()
    replication_status = IntegerField()
    path = TextField()
    expiry = DateTimeField()
