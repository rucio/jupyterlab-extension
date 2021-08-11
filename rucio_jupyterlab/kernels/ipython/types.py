# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

class DIDNotAvailableException(BaseException):
    def __init__(self):
        super().__init__("DID is not yet available.")


class MultipleItemDID(list):  # pragma: no cover
    def __init__(self, items, did_available=True):
        super(MultipleItemDID, self).__init__(items)
        self.items = items
        self.did_available = did_available

    def __str__(self):
        if not self.did_available:
            raise DIDNotAvailableException()
        return super().__str__()

    def __repr__(self):
        if not self.did_available:
            raise DIDNotAvailableException()
        return super().__repr__()

    def __getitem__(self, key):
        if not self.did_available:
            raise DIDNotAvailableException()
        return super().__getitem__(key)

    def __iter__(self):
        if not self.did_available:
            raise DIDNotAvailableException()
        return super().__iter__()


class SingleItemDID(str):  # pragma: no cover=
    def __new__(cls, path, pfn=None):
        obj = str.__new__(cls, path)
        obj.path = path
        obj.pfn = pfn
        obj.did_available = path is not None
        return obj

    def __str__(self):
        if not self.did_available:
            raise DIDNotAvailableException()
        return self.path

    def __repr__(self):
        if not self.did_available:
            raise DIDNotAvailableException()
        return self.path

    def __getitem__(self, key):
        if not self.did_available:
            raise DIDNotAvailableException()
        return super().__getitem__(key)

    def __iter__(self):
        if not self.did_available:
            raise DIDNotAvailableException()
        return super().__iter__()
