# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

def find(pred, iterable):
    for element in iterable:
        if pred(element):
            return element
    return None


def map(iterable, mapper):
    result = []
    i = 0
    for element in iterable:
        result.append(mapper(element, i))
        i += 1
    return result


def filter(iterable, filter):
    result = []
    i = 0
    for element in iterable:
        if filter(element, i):
            result.append(element)
        i += 1
    return result


def remove_none_values(dictionary):
    return {k: v for k, v in dictionary.items() if v is not None}
