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

def get_db(namespace):
    db.create_tables([Bookmark, DatasetContainerCache, FileCache])
    return NamespacedDatabaseInstance(namespace)

class NamespacedDatabaseInstance: 
    def __init__(self, namespace):
        self.namespace = namespace

    def get_bookmark(self):
        return Bookmark.select().where(Bookmark.namespace == self.namespace)

    def insert_bookmark(self, did, did_type):
        Bookmark.create(namespace=self.namespace, did=did, did_type=did_type)

    def delete_bookmark(self, did):
        bookmark = Bookmark.get(Mookmark.namespace == self.namespace and Bookmark.did == did)
        bookmark.delete_instance()

class BaseModel(Model):
    namespace = TextField()
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
