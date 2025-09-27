# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import os
import json
import tornado
import logging
from datetime import datetime, timezone
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.rucio import RucioAPI
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics

# Configure logging
logger = logging.getLogger(__name__)

class AuthConfigHandler(RucioAPIHandler):
    """
    Handler for managing Rucio authentication configurations.
    This handler allows users to retrieve and set authentication credentials
    for Rucio instances.
    The handler supports both GET and PUT methods:
    - GET: Retrieve the authentication credentials for a specified namespace and type.
    - PUT: Set or update the authentication credentials for a specified namespace and type.
    """

    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    @prometheus_metrics
    def get(self):
        namespace = self.get_query_argument('namespace')
        auth_type = self.get_query_argument('type')

        if auth_type == 'oidc':
            logger.debug("Fetching OIDC auth configuration for namespace: %s", namespace)
            instance = self.rucio.for_instance(namespace)
            # Initialize auth_credentials as an empty dictionary
            auth_credentials = {}
            # If the auth type is oidc, we need to check if the credentials are set
            # and if the oidc_auth is set to env or file
            if instance.instance_config.get('oidc_auth') == 'env':
                auth_credentials['oidc_auth_source'] = instance.instance_config.get('oidc_env_name')
            elif instance.instance_config.get('oidc_auth') == 'file':
                auth_credentials['oidc_auth_source'] = instance.instance_config.get('oidc_file_name')
            else:
                logger.error("Invalid oidc_auth configuration for namespace: %s", namespace)
                self.set_status(400)
                self.finish(json.dumps({
                    'success': False,
                    'error': 'Invalid oidc_auth configuration in instance settings. Contact your administrator.'
                }))
                return
        else:
            db = get_db()  # pylint: disable=invalid-name
            auth_credentials = db.get_rucio_auth_credentials(namespace=namespace, auth_type=auth_type)

        if auth_credentials:
            self.finish(json.dumps(auth_credentials))
        else:
            self.set_status(404)
            self.finish({'success': False, 'error': 'Auth credentials not set'})


    @tornado.web.authenticated
    @prometheus_metrics
    def put(self):
        json_body = self.get_json_body()
        namespace = json_body['namespace']
        auth_type = json_body['type']
        auth_config = json_body['params']

        db = get_db()  # pylint: disable=invalid-name
        db.set_rucio_auth_credentials(namespace=namespace, auth_type=auth_type, params=auth_config)

        RucioAPI.clear_auth_token_cache()

        # Get instance config to perform connection test
        instance = self.rucio.for_instance(namespace)
        lifetime = None  # Initialize lifetime to avoid NameError

        try:
            if auth_type == 'oidc':
                logger.debug("Handling OIDC authentication for namespace: %s", namespace)
                oidc_auth_method = instance.instance_config.get('oidc_auth')

                if oidc_auth_method not in ['env', 'file']:
                    logger.error("Invalid oidc_auth configuration for namespace: %s", namespace)
                    self.set_status(400)
                    self.finish(json.dumps({
                        'success': False,
                        'error': 'Invalid oidc_auth configuration in instance settings. Contact your administrator.'
                    }))
                    return
                # Extract token_path from auth_config
                token_path = auth_config.get('token_path', '').strip()
                
                # Only proceed if token_path is actually set to something meaningful
                if token_path != '':
                    if os.path.isfile(token_path):
                        # Read the token content
                        with open(token_path, 'r') as src_file:
                            try:
                                token_content = src_file.read()
                            except Exception as e:
                                logger.error("Error reading token file for namespace; %s, error: %s", namespace, str(e))
                                self.set_status(400)
                                self.finish(json.dumps({
                                    'success': False,
                                    'error': f'Error reading token file: {str(e)}'
                                }))
                                return
                        
                        # Write to file or env based on config
                        if instance.instance_config.get('oidc_auth') == 'file':
                            with open(instance.instance_config.get('oidc_file_name'), 'w') as dest_file:
                                dest_file.write(token_content)
                        elif instance.instance_config.get('oidc_auth') == 'env':
                            os.environ[instance.instance_config.get('oidc_env_name')] = token_content
                    else:
                        logger.error("Token path does not point to a valid file for namespace: %s", namespace)
                        self.set_status(400)
                        self.finish(json.dumps({
                            'success': False,
                            'error': 'Token path does not point to a valid file. Please provide a valid token_path.'
                        }))
                        return

            _, lifetime = RucioAPI.authenticate(instance, auth_config, auth_type)

            if auth_type == 'x509_proxy' or auth_type == 'oidc':
                # Convert to UTC datetime
                expiration_date = datetime.fromtimestamp(lifetime, tz=timezone.utc)

                # Format to ISO 8601 (can be printed directly in TSX)
                expiration_iso = expiration_date.isoformat()

                # If your TSX expects a 'Z' instead of '+00:00', you can replace it
                expiration_tsx_format = expiration_iso.replace('+00:00', 'Z')

                # If no exception, authentication was successful
                self.finish(json.dumps({'success': True, 'lifetime': expiration_tsx_format}))
            else:
                self.finish(json.dumps({'success': True}))
        except Exception as e:
            self.set_status(e.status_code or 401)

            self.finish(json.dumps({
                'success': False,
                'error': e.message,
                'exception_class': e.exception_class,
                'exception_message': e.exception_message
            }))
