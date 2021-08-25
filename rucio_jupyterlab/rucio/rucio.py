# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import logging
import time
import json
from urllib.parse import urlencode, quote
import requests
from rucio_jupyterlab.db import get_db
from .authenticators import RucioAuthenticationException, authenticate_userpass, authenticate_x509, authenticate_oidc


class RucioAPI:
    rucio_auth_token_cache = dict()

    @staticmethod
    def clear_auth_token_cache():
        RucioAPI.rucio_auth_token_cache.clear()

    def __init__(self, instance_config, auth_type, auth_config):
        self.instance_config = instance_config
        self.auth_type = auth_type
        self.auth_config = auth_config
        self.base_url = instance_config.get('rucio_base_url')
        self.auth_url = instance_config.get('rucio_auth_url', self.base_url)
        self.rucio_ca_cert = instance_config.get('rucio_ca_cert', False)    # TODO default should be True

    def get_scopes(self):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}
        response = requests.get(url=f'{self.base_url}/scopes/', headers=headers, verify=self.rucio_ca_cert)
        return response.json()

    def get_rses(self, rse_expression=None):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}

        urlencoded_params = urlencode({
            'expression': rse_expression
        })

        response = requests.get(url=f'{self.base_url}/rses?{urlencoded_params}', headers=headers, verify=self.rucio_ca_cert)

        if response.text == '':
            return []

        lines = response.text.rstrip('\n').splitlines()
        results = [json.loads(l)['rse']  for l in lines]

        return results

    def search_did(self, scope, name, search_type='collection', limit=None):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}

        scope = quote(scope)
        urlencoded_params = urlencode({
            'type': search_type,
            'long': '1',
            'name': name
        })

        response = requests.get(url=f'{self.base_url}/dids/{scope}/dids/search?{urlencoded_params}', headers=headers, verify=self.rucio_ca_cert)

        if response.text == '':
            return []

        lines = response.text.rstrip('\n').splitlines()
        results = [json.loads(l) for l in lines]

        # Apply limit, TODO: use endpoint parameter once Rucio PR #3872 is merged and released.
        if limit is not None:
            results = results[:limit]

        return results

    def get_files(self, scope, name):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}

        scope = quote(scope)
        name = quote(name)

        response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/files', headers=headers, verify=self.rucio_ca_cert)

        if response.text == '':
            return []

        lines = response.text.rstrip('\n').splitlines()
        files = [json.loads(l) for l in lines]
        return files

    def get_parents(self, scope, name):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}

        scope = quote(scope)
        name = quote(name)

        response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/parents', headers=headers, verify=self.rucio_ca_cert)

        if response.text == '':
            return []

        lines = response.text.rstrip('\n').splitlines()
        files = [json.loads(l) for l in lines]
        return files

    def get_rules(self, scope, name):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}

        scope = quote(scope)
        name = quote(name)

        response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/rules', headers=headers, verify=self.rucio_ca_cert)

        if response.text == '':
            return []

        lines = response.text.rstrip('\n').splitlines()
        rules = [json.loads(l) for l in lines]
        return rules

    def get_rule_details(self, rule_id):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}
        rule_id = quote(rule_id)
        response = requests.get(url=f'{self.base_url}/rules/{rule_id}', headers=headers, verify=self.rucio_ca_cert)
        return response.json()

    def get_replicas(self, scope, name):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}

        scope = quote(scope)
        name = quote(name)

        response = requests.get(url=f'{self.base_url}/replicas/{scope}/{name}', headers=headers, verify=self.rucio_ca_cert)

        if response.text == '':
            return []

        lines = response.text.rstrip('\n').splitlines()
        replicas = [json.loads(l) for l in lines]
        return replicas

    def add_replication_rule(self, dids, copies, rse_expression, weight=None, lifetime=None, grouping='DATASET', account=None,
                             locked=False, source_replica_expression=None, activity=None, notify='N', purge_replicas=False,
                             ignore_availability=False, comment=None, ask_approval=False, asynchronous=False, priority=3,
                             meta=None):

        data = {'dids': dids, 'copies': copies, 'rse_expression': rse_expression,
                'weight': weight, 'lifetime': lifetime, 'grouping': grouping,
                'account': account, 'locked': locked, 'source_replica_expression': source_replica_expression,
                'activity': activity, 'notify': notify, 'purge_replicas': purge_replicas,
                'ignore_availability': ignore_availability, 'comment': comment, 'ask_approval': ask_approval,
                'asynchronous': asynchronous, 'priority': priority, 'meta': meta}

        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}

        response = requests.post(url=f'{self.base_url}/rules/', headers=headers, json=data, verify=self.rucio_ca_cert)
        return response.json()

    def _get_auth_token(self):
        config = self.instance_config
        instance_name = config.get('name')
        cached_token = self._get_cached_token(instance_name)
        if cached_token:
            return cached_token

        token, expiry = self._authenticate()
        RucioAPI.rucio_auth_token_cache[instance_name] = (token, expiry)
        return token

    def _get_cached_token(self, instance):
        if instance in RucioAPI.rucio_auth_token_cache:
            token_cache, expiry = RucioAPI.rucio_auth_token_cache[instance]
            if int(expiry) > int(time.time()):
                return token_cache

        return None

    def _authenticate(self):
        auth_config = self.auth_config
        auth_type = self.auth_type

        if not auth_type:
            raise RucioAuthenticationException()

        logging.info('Attempting to authenticate using method %s...', auth_type)

        app_id = self.instance_config.get('app_id')
        vo = self.instance_config.get('vo')

        if auth_type == 'userpass':
            username = auth_config.get('username')
            password = auth_config.get('password')
            account = auth_config.get('account')

            return authenticate_userpass(base_url=self.auth_url, username=username, password=password, account=account, vo=vo, app_id=app_id, rucio_ca_cert=self.rucio_ca_cert)
        elif auth_type == 'x509':
            cert_path = auth_config.get('certificate')
            key_path = auth_config.get('key')
            account = auth_config.get('account')

            return authenticate_x509(base_url=self.auth_url, cert_path=cert_path, key_path=key_path, account=account, vo=vo, app_id=app_id, rucio_ca_cert=self.rucio_ca_cert)
        elif auth_type == 'x509_proxy':
            proxy = auth_config.get('proxy')
            account = auth_config.get('account')

            return authenticate_x509(base_url=self.auth_url, cert_path=proxy, key_path=proxy, account=account, vo=vo, app_id=app_id, rucio_ca_cert=self.rucio_ca_cert)

        elif auth_type == 'oidc':
            oidc_auth = self.instance_config.get('oidc_auth')
            oidc_auth_source = self.instance_config.get('oidc_env_name') if oidc_auth == 'env' else self.instance_config.get('oidc_file_name')

            return authenticate_oidc(base_url=self.base_url, oidc_auth=oidc_auth, oidc_auth_source=oidc_auth_source, rucio_ca_cert=self.rucio_ca_cert)

        return None


class RucioAPIFactory:  # pragma: no cover
    def __init__(self, config):
        self.config = config

    def for_instance(self, instance):
        instance_config = self.config.get_instance_config(instance)
        db = get_db()   # pylint: disable=invalid-name

        auth_type = db.get_active_auth_method()
        if not auth_type:
            auth_type = self.config.get_default_auth_type()

        auth_config = db.get_rucio_auth_credentials(instance, auth_type)

        return RucioAPI(instance_config=instance_config, auth_type=auth_type, auth_config=auth_config)
