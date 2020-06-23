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

    def set_file_replica(self, namespace, file_did, pfn, size):
        pass
