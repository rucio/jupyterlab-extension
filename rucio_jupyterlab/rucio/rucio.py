# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import logging
import re
import time
import json
from urllib.parse import urlencode, quote
import requests
from rucio_jupyterlab.db import get_db
from .authenticators import RucioAuthenticationException, authenticate_userpass, authenticate_x509, authenticate_oidc


def parse_did_filter_from_string_fe(input_string, name='*', type='collection', omit_name=False):
    """
    Parse DID filter string for the filter engine (fe).

    Should adhere to the following conventions:
    - ';' represents the logical OR operator
    - ',' represents the logical AND operator
    - all operators belong to set of (<=, >=, ==, !=, >, <, =)
    - there should be no duplicate key+operator criteria.

    One sided and compound inequalities are supported.

    Sanity checking of input is left to the filter engine.

    :param input_string: String containing the filter options.
    :param name: DID name.
    :param type: The type of the did: all(container, dataset, file), collection(dataset or container), dataset, container.
    :param omit_name: omit addition of name to filters.
    :return: list of dictionaries with each dictionary as a separate OR expression.
    """
    # lookup table unifying all comprehended operators to a nominal suffix.
    # note that the order matters as the regex engine is eager, e.g. don't want to evaluate '<=' as '<' and '='.
    operators_suffix_LUT = dict({
        '≤': 'lte',
        '≥': 'gte',
        '==': '',
        '≠': 'ne',
        '>': 'gt',
        '<': 'lt',
        '=': ''
    })

    # lookup table mapping operator opposites, used to reverse compound inequalities.
    operator_opposites_LUT = {
        'lt': 'gt',
        'lte': 'gte'
    }
    operator_opposites_LUT.update({op2: op1 for op1, op2 in operator_opposites_LUT.items()})

    filters = []
    if input_string:
        or_groups = list(filter(None, input_string.split(';')))     # split <input_string> into OR clauses
        for or_group in or_groups:
            or_group = or_group.strip()
            and_groups = list(filter(None, or_group.split(',')))    # split <or_group> into AND clauses
            and_group_filters = {}
            for and_group in and_groups:
                and_group = and_group.strip()
                # tokenise this AND clause using operators as delimiters.
                tokenisation_regex = "({})".format('|'.join(operators_suffix_LUT.keys()))
                and_group_split_by_operator = list(filter(None, re.split(tokenisation_regex, and_group)))
                if len(and_group_split_by_operator) == 3:       # this is a one-sided inequality or expression
                    key, operator, value = [token.strip() for token in and_group_split_by_operator]

                    # substitute input operator with the nominal operator defined by the LUT, <operators_suffix_LUT>.
                    operator_mapped = operators_suffix_LUT.get(operator)

                    filter_key_full = key = "'{}'".format(key)
                    if operator_mapped is not None:
                        if operator_mapped:
                            filter_key_full = "{}.{}".format(key, operator_mapped)
                    else:
                        raise ValueError("{} operator not understood.".format(operator_mapped))

                    if filter_key_full in and_group_filters:
                        raise ValueError(filter_key_full)
                    else:
                        if not is_numeric(value):
                            value = "'{}'".format(value)
                        and_group_filters[filter_key_full] = value
                elif len(and_group_split_by_operator) == 5:     # this is a compound inequality
                    value1, operator1, key, operator2, value2 = [token.strip() for token in and_group_split_by_operator]

                    # substitute input operator with the nominal operator defined by the LUT, <operators_suffix_LUT>.
                    operator1_mapped = operator_opposites_LUT.get(operators_suffix_LUT.get(operator1))
                    operator2_mapped = operators_suffix_LUT.get(operator2)

                    key = "'{}'".format(key)
                    filter_key1_full = filter_key2_full = key
                    if operator1_mapped is not None and operator2_mapped is not None:
                        if operator1_mapped:    # ignore '' operator (maps from equals)
                            filter_key1_full = "{}.{}".format(key, operator1_mapped)
                        if operator2_mapped:    # ignore '' operator (maps from equals)
                            filter_key2_full = "{}.{}".format(key, operator2_mapped)
                    else:
                        raise ValueError("{} operator not understood.".format(operator_mapped))

                    if filter_key1_full in and_group_filters:
                        raise ValueError(filter_key1_full)
                    else:
                        if not is_numeric(value1):
                            value1 = "'{}'".format(value1)
                        and_group_filters[filter_key1_full] = value1
                    if filter_key2_full in and_group_filters:
                        raise ValueError(filter_key2_full)
                    else:
                        if not is_numeric(value2):
                            value2 = "'{}'".format(value2)
                        and_group_filters[filter_key2_full] = value2
                else:
                    raise ValueError(and_group)

            # add name key to each AND clause if it hasn't already been populated from the filter and <omit_name> not set.
            if not omit_name and 'name' not in and_group_filters:
                and_group_filters['name'] = name

            filters.append(and_group_filters)
    else:
        if not omit_name:
            filters.append({
                'name': name
            })
    return filters, type


def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


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

    def search_did(self, scope, name, search_type='collection', filters=None, limit=None):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}

        scope = quote(scope)
        params = {
            'type': search_type,
            'long': '1',
            'name': name
        }
        if filters:
            filters, _ = parse_did_filter_from_string_fe(filters)
            params['filters'] = filters
        urlencoded_params = urlencode(params)

        response = requests.get(url=f'{self.base_url}/dids/{scope}/dids/search?{urlencoded_params}', headers=headers, verify=self.rucio_ca_cert)

        if response.text == '':
            return []

        lines = response.text.rstrip('\n').splitlines()
        results = [json.loads(l) for l in lines]

        # Apply limit, TODO: use endpoint parameter once Rucio PR #3872 is merged and released.
        if limit is not None:
            results = results[:limit]

        return results

    def get_metadata(self, scope, name):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}

        scope = quote(scope)
        name = quote(name)

        response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/meta', headers=headers, verify=self.rucio_ca_cert)

        if response.text == '':
            return []

        lines = response.text.rstrip('\n').splitlines()
        results = [json.loads(l) for l in lines]

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
