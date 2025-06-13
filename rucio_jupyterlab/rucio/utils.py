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
import os, errno
import logging

logger = logging.getLogger(__name__)

def parse_timestamp(timestr):
    time_struct = time.strptime(timestr, '%a, %d %b %Y %H:%M:%S %Z')
    return int(calendar.timegm(time_struct))


def get_oidc_token(oidc_auth, oidc_auth_source):
    try:
        if oidc_auth == 'env':
            if oidc_auth_source not in os.environ:
                raise KeyError(f"Environment variable '{oidc_auth_source}' not found.")
            return os.environ[oidc_auth_source]
        elif oidc_auth == 'file':
            if not os.path.exists(oidc_auth_source):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), cert_path)
            with open(oidc_auth_source) as f:
                return f.read()
    except FileNotFoundError as e:
        logger.error(f"Token file not found: {oidc_auth_source}")
        raise FileNotFoundError(e)
    except KeyError as e:
        logger.error(f"Environment variable not found: {oidc_auth_source}")
        raise KeyError(e)