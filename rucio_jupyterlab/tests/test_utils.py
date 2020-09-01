# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import rucio_jupyterlab.utils as utils


def test_filter_elements_exist():
    haystack = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    expected_result = [2, 4, 6, 8, 0]

    assert utils.filter(haystack, lambda x, _: x % 2 == 0) == expected_result, "Invalid return value"


def test_filter_elements_not_exist():
    haystack = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    expected_result = []

    assert utils.filter(haystack, lambda x, _: False) == expected_result, "Invalid return value"


def test_filter_iterable_empty():
    haystack = []
    expected_result = []

    assert utils.filter(haystack, lambda x, _: True) == expected_result, "Invalid return value"


def test_find_element_exists():
    haystack = [
        {'name': 'Alice', 'role': 'sender'},
        {'name': 'Bob', 'role': 'recipient'},
        {'name': 'Eve', 'role': 'eavesdropper'},
        {'name': 'Mallory', 'role': 'malicious_person'}
    ]
    expected_result = {'name': 'Bob', 'role': 'recipient'}

    assert utils.find(lambda x: x['name'] == 'Bob', haystack) == expected_result, "Invalid return value"


def test_find_element_not_exists():
    haystack = [
        {'name': 'Alice', 'role': 'sender'},
        {'name': 'Bob', 'role': 'recipient'},
        {'name': 'Eve', 'role': 'eavesdropper'},
        {'name': 'Mallory', 'role': 'malicious_person'}
    ]
    expected_result = None

    assert utils.find(lambda x: x['name'] == 'Wangky', haystack) == expected_result, "Invalid return value"


def test_map():
    iterable = [1, 2, 3, 4, 5, 6, 7, 8]
    expected_result = [2, 3, 4, 5, 6, 7, 8, 9]

    assert utils.map(iterable, lambda x, _: x + 1) == expected_result, "Invalid return value"
