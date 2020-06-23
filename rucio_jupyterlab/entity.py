class BaseEntity:
    def to_dict(self):
        return self.__dict__


class AttachedFile(BaseEntity):
    def __init__(self, did, size):
        self.did = did
        self.size = size


class FileReplica(BaseEntity):
    def __init__(self, did, path, size):
        self.did = did
        self.size = size
        self.path = path


class PfnFileReplica(BaseEntity):
    def __init__(self, did, pfn, size):
        self.did = did
        self.size = size
        self.pfn = pfn
