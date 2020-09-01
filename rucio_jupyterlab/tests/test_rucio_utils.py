# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from rucio_jupyterlab.rucio.utils import parse_timestamp


def test_parse_timestamp_returns_correct_timezone_utc():
    time_str = 'Mon, 13 May 2013 10:23:03 UTC'
    expected_output = 1368440583
    assert parse_timestamp(time_str) == expected_output, "Invalid timestamp conversion"
