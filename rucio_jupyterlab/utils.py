# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

from rucio_jupyterlab.db import get_db
from tornado.web import HTTPError

def find(pred, iterable):
    """Finds the first element in an iterable for which a predicate is true."""
    for element in iterable:
        if pred(element):
            return element
    return None


def map(iterable, mapper):
    """Maps an iterable to a new list, providing each element and its index to the mapper function."""
    result = []
    i = 0
    for element in iterable:
        result.append(mapper(element, i))
        i += 1
    return result


def filter(iterable, predicate):
    """Filters an iterable, keeping elements for which the predicate (given element and index) is true."""
    result = []
    i = 0
    for element in iterable:
        if predicate(element, i):
            result.append(element)
        i += 1
    return result


def remove_none_values(dictionary):
    """Removes key-value pairs from a dictionary where the value is None."""
    return {k: v for k, v in dictionary.items() if v is not None}

def ensure_credentials_present(rucio_config, instance_name):
    """Ensure authentication credentials exist for the given instance."""
    db = get_db()
    # Check for ANY stored credentials for this instance
    has_creds = db.has_any_auth_credentials(namespace=instance_name)

    if not has_creds:
        raise HTTPError(
            status_code=401,
            reason="Credentials not found. Did you authenticate?"
        )
