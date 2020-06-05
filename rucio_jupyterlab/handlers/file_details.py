import os
import time
import tornado
import json
import itertools
from urllib.parse import urlparse
from .base import RucioAPIHandler
from rucio_jupyterlab.db import get_namespaced_db
from rucio_jupyterlab.rucio.utils import parse_timestamp


class FileDetailsHandler(RucioAPIHandler):
    STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
    STATUS_REPLICATING = "REPLICATING"
    STATUS_OK = "OK"
    STATUS_STUCK = "STUCK"

    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        poll = self.get_query_argument('poll', 0) != 0
        did = self.get_query_argument('did')
        scope, name = did.split(':')

        if poll:
            output = self.poll_status(namespace, scope, name)
        else:
            output = self.get_file_details(namespace, scope, name)
        self.finish(json.dumps(output))

    def get_file_details(self, namespace, scope, name):
        rucio = self.rucio.for_instance(namespace)
        db = get_namespaced_db(namespace)
        file_did = f'{scope}:{name}'

        from_cache = self.from_cache(db, file_did)
        if from_cache:
            return from_cache

        file_details = self.fetch_file_details(rucio, scope, name)
        if file_details:
            return self.file_available(db, file_did, file_details)

        return self.file_unavailable(db, file_did)

    def poll_status(self, namespace, scope, name):
        rucio = self.rucio.for_instance(namespace)
        db = get_namespaced_db(namespace)
        file_did = f'{scope}:{name}'

        from_cache = self.from_cache(db, file_did)
        if from_cache:
            rule_id = from_cache.get('replication_rule_id')
        else:
            rule_id = None

        file_details = self.fetch_file_details(
            rucio, scope, name, rule_id=rule_id)

        if file_details:
            return self.file_available(db, file_did, file_details)

        return self.file_unavailable(db, file_did)

    def from_cache(self, db, file_did):
        cached_file_did = db.get_cached_file_details(file_did)
        if cached_file_did:
            if cached_file_did.path:
                if self.check_path_exists(cached_file_did.path):
                    return dict(
                        status=cached_file_did.replication_status,
                        replication_rule_id=cached_file_did.replication_rule_id,
                        path=cached_file_did.path
                    )
            else:
                return dict(status=cached_file_did.replication_status, replication_rule_id=None, path=None)

        return None

    def file_unavailable(self, db, file_did):
        db.set_cached_file_details(
            file_did, replication_status=FileDetailsHandler.STATUS_NOT_AVAILABLE)
        return dict(status=FileDetailsHandler.STATUS_NOT_AVAILABLE, replication_rule_id=None, path=None)

    def file_available(self, db, file_did, file_details):
        status = file_details.get('status')
        rule_id = file_details.get('rule_id')
        path = file_details.get('path')
        expiry = file_details.get('expires_at')

        db.set_cached_file_details(file_did, replication_status=status,
                                   replication_rule_id=rule_id, path=path, expiry=expiry)

        return dict(status=status, path=path, replication_rule_id=rule_id)

    def check_path_exists(self, path):
        if not path:
            return False

        return os.path.isfile(path)

    def fetch_file_details(self, rucio, scope, name, rule_id=None):
        if rule_id:
            replication_rule = self.fetch_replication_rule(rule_id)
        else:
            replication_rule = self.fetch_relevant_replication_rule(
                rucio, scope, name)

        if not replication_rule:
            return None

        rule_id, status, expires_at = replication_rule
        if status == FileDetailsHandler.STATUS_OK:
            pfn = self.fetch_pfn(rucio, scope, name)

            if pfn:
                file_did = scope + ':' + name
                path = self.translate_pfn_to_path(rucio, pfn)
                return dict(status=status, path=path, rule_id=rule_id, expires_at=expires_at)

        return dict(status=status, rule_id=rule_id, expires_at=expires_at)

    def fetch_relevant_replication_rule(self, rucio, scope, name):
        destination_rse = rucio.instance_config.get('destination_rse')

        rules = rucio.get_rules(scope, name)
        filtered_rules = []
        for rule in rules:
            if rule['rse_expression'] == destination_rse:
                filtered_rules.append(rule)

        if len(filtered_rules) > 0:
            replication_rule = filtered_rules[0]
            rule_id = replication_rule.get('id')
            status = self.parse_rule_status(replication_rule.get('state'))
            expires_at = replication_rule.get('expires_at')

            return (rule_id, status, expires_at)

        return None

    def fetch_replication_rule(self, rucio, rule_id):
        destination_rse = rucio.instance_config.get('destination_rse')

        rule = rucio.get_rule_details()
        if not rule:
            return None

        if rule.get('rse_expression') != destination_rse:
            return None

        rule_id = rule.get('id')
        status = self.parse_rule_status(rule.get('state'))
        expires_at = rule.get('expires_at')

        return (rule_id, status, expires_at)

    def parse_rule_status(self, status):
        if status == 'OK':
            status = FileDetailsHandler.STATUS_OK
        elif status == 'REPLICATING':
            status = FileDetailsHandler.STATUS_REPLICATING
        else:
            status = FileDetailsHandler.STATUS_STUCK

        return status

    def fetch_pfn(self, rucio, scope, name):
        destination_rse = rucio.instance_config.get('destination_rse')

        replicas = rucio.get_replicas(scope, name)
        rses = replicas['rses']
        states = replicas['states']

        if (destination_rse in rses) and (destination_rse in states):
            if states[destination_rse] == 'AVAILABLE':
                pfns = rses[destination_rse]
                if len(pfns) > 0:
                    return pfns[0]

        return None

    def translate_pfn_to_path(self, rucio, pfn):
        instance_config = rucio.instance_config
        prefix_path = instance_config.get('rse_mount_path')
        path_begins_at = instance_config.get('path_begins_at', 0)

        path = urlparse(pfn).path
        suffix_path = self.get_path_after_nth_slash(path, path_begins_at)
        return os.path.join(prefix_path, suffix_path)

    def get_path_after_nth_slash(self, path, n):
        return path.strip('/').split('/', n)[-1]
