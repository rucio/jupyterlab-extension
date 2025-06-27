# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025
# - Enrique Garcia, <enrique.garcia.garcia@cern.ch>, 2025

import logging
import re
import time
import json
from urllib.parse import urlencode, quote
import requests
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.rucio.authenticators import authenticate_userpass, authenticate_x509, authenticate_oidc
from rucio_jupyterlab.rucio.exceptions import RucioAPIException, RucioAuthenticationException, RucioRequestsException, RucioHTTPException


# Setup logging
logger = logging.getLogger(__name__)


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
    OPERATORS_SUFFIX_LUT = dict({  # Being this a lookup table, we define a constant.
        '≤': 'lte',
        '≥': 'gte',
        '==': '',
        '≠': 'ne',
        '>': 'gt',
        '<': 'lt',
        '=': ''
    })

    # lookup table mapping operator opposites, used to reverse compound inequalities.
    OPERATORS_OPPOSITES_LUT = {  # Being this a lookup table, we define a constant.
        'lt': 'gt',
        'lte': 'gte'
    }
    OPERATORS_OPPOSITES_LUT.update({op2: op1 for op1, op2 in OPERATORS_OPPOSITES_LUT.items()})

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
                tokenisation_regex = "({})".format('|'.join(OPERATORS_SUFFIX_LUT.keys()))
                and_group_split_by_operator = list(filter(None, re.split(tokenisation_regex, and_group)))
                if len(and_group_split_by_operator) == 3:       # this is a one-sided inequality or expression
                    key, operator, value = [token.strip() for token in and_group_split_by_operator]

                    # substitute input operator with the nominal operator defined by the LUT, <OPERATORS_SUFFIX_LUT>.
                    operator_mapped = OPERATORS_SUFFIX_LUT.get(operator)

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

                    # substitute input operator with the nominal operator defined by the LUT, <OPERATORS_SUFFIX_LUT>.
                    operator1_mapped = OPERATORS_OPPOSITES_LUT.get(OPERATORS_SUFFIX_LUT.get(operator1))
                    operator2_mapped = OPERATORS_SUFFIX_LUT.get(operator2)

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
        self.rucio_ca_cert = instance_config.get('rucio_ca_cert', True)    # Default should be True to use system CA certs

    def _build_url(self, endpoint, scope=None, name=None, params=None):
        """
        Constructs the full URL with optional scope, name and params.
        """
        url_parts = [self.base_url]
        if endpoint:
            url_parts.append(endpoint)
        if scope:
            url_parts.append(quote(scope))
        if name:
            url_parts.append(quote(name))
        url = '/'.join(url_parts)
        if params:
            url = f"{url}?{urlencode(params)}"
        return url

    def _make_rucio_request(self, method, endpoint, scope=None, name=None, params=None, data=None,
                            parse_json=False, parse_lines=False):
        """
        Centralizes logic for making Rucio API requests and handling errors.
        """
        url = self._build_url(endpoint, scope, name, params)

        try:
            token = self._get_auth_token()
            headers = {'X-Rucio-Auth-Token': token}

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                verify=self.rucio_ca_cert
            )
            logger.debug("RucioAPI: %s request to %s with headers: %s and params: %s", method.upper(), url, headers, params)
            logger.debug("Response status code: %s, response text: %s", response.status_code, response.text)

            response.raise_for_status()

            if parse_json:
                if parse_lines:
                    if response.text.strip():
                        return [json.loads(line) for line in response.text.strip().splitlines()]
                    else:
                        return []
                return response.json() if response.text else {}
            else:
                return response.text

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error for %s request to %s: %s %s", method.upper(), url, e.response.status_code, e.response.reason)
            raise RucioHTTPException(e.response)

        except requests.exceptions.RequestException as e:
            # For other requests-related errors like connection, timeout
            logger.error("Request error for %s request to %s: %s", method.upper(), url, str(e))
            raise RucioRequestsException(None, str(e))

        except Exception as e:
            # For errors unrelated to requests itself (e.g., JSON parse)
            logger.error("An error occurred during the %s request to %s: %s", method.upper(), url, str(e))
            raise RucioAPIException(None, str(e))

    def get_scopes(self):
        # DEBUG: response = requests.get(url=f'{self.base_url}/scopes/', headers=headers, verify=self.rucio_ca_cert)
        return self._make_rucio_request('GET', 'scopes/', parse_json=True)

    def get_rses(self, rse_expression=None):
        # DEBUG: response = requests.get(url=f'{self.base_url}/rses?{urlencoded_params}', headers=headers, verify=self.rucio_ca_cert)
        params = {'expression': rse_expression} if rse_expression else None
        return self._make_rucio_request('GET', 'rses', params=params, parse_json=True, parse_lines=True)

    def search_did(self, scope, name, search_type='collection', filters=None, limit=None):
        # DEBUG: response = requests.get(url=f'{self.base_url}/dids/{scope}/dids/search?{urlencoded_params}', headers=headers, verify=self.rucio_ca_cert)
        params = {
            'type': search_type,
            'long': '1',
            'name': name
        }
        if filters:
            filters, _ = parse_did_filter_from_string_fe(filters, name=name)
            params['filters'] = filters

        results = self._make_rucio_request(
            'GET',
            f'dids/{scope}/dids/search',
            params=params,
            parse_json=True,
            parse_lines=True
        )
        if limit is not None:
            results = results[:limit]
        return results

    def get_metadata(self, scope, name):
        # DEBUG: response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/meta', headers=headers, verify=self.rucio_ca_cert)
        return self._make_rucio_request('GET', 'dids', scope, name + '/meta', parse_lines=True)

    def get_files(self, scope, name):
        # DEBUG: response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/files', headers=headers, verify=self.rucio_ca_cert)
        return self._make_rucio_request('GET', 'dids', scope, name + '/files', parse_json=True, parse_lines=True)

    def get_parents(self, scope, name):
        # DEBUG: response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/parents', headers=headers, verify=self.rucio_ca_cert)
        return self._make_rucio_request('GET', 'dids', scope, name + '/parents', parse_json=True, parse_lines=True)

    def get_rules(self, scope, name):
        # DEBUG: response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/rules', headers=headers, verify=self.rucio_ca_cert)
        return self._make_rucio_request('GET', 'dids', scope, name + '/rules', parse_json=True, parse_lines=True)

    def get_rule_details(self, rule_id):
        # DEBUG: response = requests.get(url=f'{self.base_url}/rules/{rule_id}', headers=headers, verify=self.rucio_ca_cert)
        return self._make_rucio_request('GET', 'rules', rule_id, parse_json=True)

    def get_replicas(self, scope, name):
        # DEBUG: response = requests.get(url=f'{self.base_url}/replicas/{scope}/{name}', headers=headers, verify=self.rucio_ca_cert)
        return self._make_rucio_request('GET', 'replicas', scope, name, parse_json=True, parse_lines=True)

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

        token, expiry = self.authenticate(self.auth_config, self.auth_type)
        RucioAPI.rucio_auth_token_cache[instance_name] = (token, expiry)
        return token

    def _get_cached_token(self, instance):
        if instance in RucioAPI.rucio_auth_token_cache:
            token_cache, expiry = RucioAPI.rucio_auth_token_cache[instance]
            if int(expiry) > int(time.time()):
                return token_cache

        return None

    def authenticate(self, auth_config, auth_type):

        if not auth_type:
            raise RucioAuthenticationException()

        logger.info('Attempting to authenticate using method %s...', auth_type)

        app_id = self.instance_config.get('app_id')
        vo = self.instance_config.get('vo')
        try:
            if auth_type == 'userpass':
                username = auth_config.get('username')
                password = auth_config.get('password')
                account = auth_config.get('account')

                # TODO VO is currently not accepted by the userpass authenticator, so we pass None
                return authenticate_userpass(base_url=self.auth_url, username=username, password=password, account=account, vo=None, app_id=app_id, rucio_ca_cert=self.rucio_ca_cert)
            elif auth_type == 'x509':
                cert_path = auth_config.get('certificate')
                key_path = auth_config.get('key')
                account = auth_config.get('account')

                # TODO VO is currently not accepted by the x509 authenticator, so we pass None
                return authenticate_x509(base_url=self.auth_url, cert_path=cert_path, key_path=key_path, account=account, vo=None, app_id=app_id, rucio_ca_cert=self.rucio_ca_cert)
            elif auth_type == 'x509_proxy':
                proxy = auth_config.get('proxy')
                account = auth_config.get('account')

                # TODO VO is currently not accepted by the x509_proxy authenticator, so we pass None
                return authenticate_x509(base_url=self.auth_url, cert_path=proxy, key_path=proxy, account=account, vo=None, app_id=app_id, rucio_ca_cert=self.rucio_ca_cert)

            elif auth_type == 'oidc':
                oidc_auth = self.instance_config.get('oidc_auth')
                oidc_auth_source = self.instance_config.get('oidc_env_name') if oidc_auth == 'env' else self.instance_config.get('oidc_file_name')

                return authenticate_oidc(base_url=self.base_url, oidc_auth=oidc_auth, oidc_auth_source=oidc_auth_source, rucio_ca_cert=self.rucio_ca_cert)

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error during authentication for %s: %s %s", auth_type, e.response.status_code, e.response.reason)
            raise RucioHTTPException(e.response)

        except requests.exceptions.RequestException as e:
            # For other requests-related errors like connection, timeout
            logger.error("Request error during authentication for %s: %s", auth_type, str(e))
            raise RucioRequestsException(None, str(e))

        except Exception as e:
            # For errors unrelated to requests itself (e.g., JSON parse)
            logger.error("An error occurred during authentication for %s: %s", auth_type, str(e))
            raise RucioAPIException(None, str(e))

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
