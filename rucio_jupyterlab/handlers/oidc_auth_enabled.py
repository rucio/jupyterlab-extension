# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021

import json
import tornado
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.rucio import RucioAPI
from rucio_jupyterlab.rucio.utils import get_oidc_token
from rucio_jupyterlab.rucio.authenticators import RucioAuthenticationException, authenticate_oidc
from .base import RucioAPIHandler


class OIDCAuthEnabledHandler(RucioAPIHandler):

    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        rucio_instance = self.rucio.for_instance(namespace)

        oidc_auth = rucio_instance.instance_config.get('oidc_auth')
        oidc_auth_source = rucio_instance.instance_config.get('oidc_env_name') if oidc_auth == 'env' else rucio_instance.instance_config.get('oidc_file_name')

        if oidc_auth is None or oidc_auth_source is None:
            self.finish({'enabled': False})
            return

        oidc_token = get_oidc_token(oidc_auth, oidc_auth_source)
        oidc_enabled = oidc_token is not None
        self.finish({'enabled': oidc_enabled})
