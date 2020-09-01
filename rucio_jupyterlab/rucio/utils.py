# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import time
import calendar


def parse_timestamp(timestr):
    time_struct = time.strptime(timestr, '%a, %d %b %Y %H:%M:%S %Z')
    return int(calendar.timegm(time_struct))
