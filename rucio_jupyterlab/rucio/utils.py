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
import os
import errno
import logging

logger = logging.getLogger(__name__)


def parse_timestamp(timestr):
    time_struct = time.strptime(timestr, '%a, %d %b %Y %H:%M:%S %Z')
    return int(calendar.timegm(time_struct))


def get_oidc_token(oidc_auth, oidc_auth_source):
    try:
        if oidc_auth == 'env':
            if oidc_auth_source not in os.environ:
                logger.error(f"Environment variable not found: {oidc_auth_source}")
                return None
            return os.environ[oidc_auth_source]
        elif oidc_auth == 'file':
            if not os.path.exists(oidc_auth_source):
                logger.error(f"Token file not found: {oidc_auth_source}")
                return None
            with open(oidc_auth_source) as f:
                return f.read()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
    return None
