import logging
import time
import json
import requests
from .authenticators import authenticate_userpass


class RucioAPI:
    rucio_auth_token_cache = dict()

    def __init__(self, instance_config):
        self.instance_config = instance_config
        self.base_url = instance_config.get('rucio_base_url')

    def get_files(self, scope, name):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}
        response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/files',
                                headers=headers, verify=False)    # TODO verify=True
        lines = response.text.splitlines()
        files = [json.loads(l) for l in lines]
        return files

    def get_rules(self, scope, name):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}
        response = requests.get(url=f'{self.base_url}/dids/{scope}/{name}/rules',
                                headers=headers, verify=False)    # TODO verify=True
        lines = response.text.splitlines()
        rules = [json.loads(l) for l in lines]
        return rules

    def get_rule_details(self, rule_id):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}
        response = requests.get(
            url=f'{self.base_url}/rules/{rule_id}', headers=headers, verify=False)    # TODO verify=True
        return response.json()

    def get_replicas(self, scope, name):
        token = self._get_auth_token()
        headers = {'X-Rucio-Auth-Token': token}
        response = requests.get(url=f'{self.base_url}/replicas/{scope}/{name}',
                                headers=headers, verify=False)    # TODO verify=True
        return response.json()

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

        response = requests.post(url=f'{self.base_url}/rules/', headers=headers, json=data, verify=False)
        return response.json()

    def _get_auth_token(self):
        config = self.instance_config
        instance_name = config.get('name')
        cached_token = self._get_cached_token(instance_name)
        if cached_token:
            return cached_token
        else:
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
        auth_config = self.instance_config.get('auth')
        auth_type = auth_config.get('type')

        logging.info(
            'Attempting to authenticate using method %s...', auth_type)

        if auth_type == 'userpass':
            username = auth_config.get('username')
            password = auth_config.get('password')
            account = auth_config.get('account')
            app_id = auth_config.get('app_id')

            return authenticate_userpass(base_url=self.base_url, username=username, password=password, account=account, app_id=app_id)
        else:
            return None


class RucioAPIFactory:
    def __init__(self, config):
        self.config = config

    def for_instance(self, instance):
        instance_config = self.config.get_instance_config(instance)
        return RucioAPI(instance_config=instance_config)
