# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

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
