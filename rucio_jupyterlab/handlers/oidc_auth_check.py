# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import tornado
from .base import RucioAPIHandler
from rucio_jupyterlab.rucio.authenticators import RucioAuthenticationException, authenticate_oidc


class OIDCAuthCheckHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            namespace = self.get_query_argument('namespace')
            rucio_instance = self.rucio.for_instance(namespace)

            base_url = rucio_instance.base_url
            rucio_ca_cert = rucio_instance.rucio_ca_cert
            oidc_auth = rucio_instance.instance_config.get('oidc_auth')
            oidc_auth_source = rucio_instance.instance_config.get('oidc_env_name') if oidc_auth == 'env' else rucio_instance.instance_config.get('oidc_file_name')

            _, expires = authenticate_oidc(base_url=base_url, oidc_auth=oidc_auth, oidc_auth_source=oidc_auth_source, rucio_ca_cert=rucio_ca_cert)

            self.finish({'success': True, 'oidc_auth': oidc_auth, 'oidc_auth_source': oidc_auth_source, 'expires': expires})
        except RucioAuthenticationException:
            self.set_status(403)
            self.finish({'success': False, 'error': 'OpenID Connect token is expired or invalid. Try logging out and logging back in.'})
