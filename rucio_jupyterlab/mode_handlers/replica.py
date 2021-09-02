# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import os
from urllib.parse import urlparse
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile, PfnFileReplica
import rucio_jupyterlab.utils as utils


class ReplicaModeHandler:
    STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
    STATUS_REPLICATING = "REPLICATING"
    STATUS_OK = "OK"
    STATUS_STUCK = "STUCK"

    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name

    def make_available(self, scope, name):
        dids = [{'scope': scope, 'name': name}]
        destination_rse = self.rucio.instance_config.get('destination_rse')
        lifetime_days = self.rucio.instance_config.get('replication_rule_lifetime_days')
        lifetime = (lifetime_days * 60 * 60 * 24) if lifetime_days else None
        return self.rucio.add_replication_rule(dids=dids, rse_expression=destination_rse, copies=1, lifetime=lifetime)

    def get_did_details(self, scope, name, force_fetch=False):
        attached_file_replicas = self.get_attached_file_replicas(scope, name, force_fetch)
        complete = utils.find(lambda x: x.pfn is None, attached_file_replicas) is None

        status = ReplicaModeHandler.STATUS_NOT_AVAILABLE
        if not complete:
            status = self.get_did_status(scope, name)

        def result_mapper(file_replica, _):
            file_did = file_replica.did
            pfn = file_replica.pfn
            path = self.translate_pfn_to_path(pfn) if pfn else None
            size = file_replica.size

            if path is None:
                # This is to handle newly-attached files in which the replication rule hasn't been reevaluated by the judger daemon.
                result_status = status if status != ReplicaModeHandler.STATUS_OK else ReplicaModeHandler.STATUS_REPLICATING
                return dict(status=result_status, did=file_did, path=None, size=size, pfn=pfn)

            return dict(status=ReplicaModeHandler.STATUS_OK, did=file_did, path=path, size=size, pfn=pfn)

        results = utils.map(attached_file_replicas, result_mapper)
        return results

    def get_attached_file_replicas(self, scope, name, force_fetch=False):
        did = scope + ':' + name
        attached_files = self.db.get_attached_files(self.namespace, did) if not force_fetch else None

        pfn_file_replicas = self.get_all_pfn_file_replicas_from_db(attached_files) if attached_files else None

        if pfn_file_replicas is None:
            pfn_file_replicas = self.fetch_attached_pfn_file_replicas(scope, name)

        return pfn_file_replicas

    def get_all_pfn_file_replicas_from_db(self, attached_files):
        pfn_file_replicas = []
        for attached_file in attached_files:
            file_did = attached_file.did
            db_file_replica = self.db.get_file_replica(self.namespace, file_did)

            if db_file_replica is None:
                return None

            pfn_file_replica = PfnFileReplica(did=db_file_replica.did, pfn=db_file_replica.pfn, size=db_file_replica.size)
            pfn_file_replicas.append(pfn_file_replica)

        return pfn_file_replicas

    def fetch_attached_pfn_file_replicas(self, scope, name):
        pfn_file_replicas = []
        attached_dids = []
        fetched_file_replicas = self.fetch_file_replicas(scope, name)
        for pfn_file_replica in fetched_file_replicas:
            self.db.set_file_replica(self.namespace, file_did=pfn_file_replica.did, pfn=pfn_file_replica.pfn, size=pfn_file_replica.size)
            pfn_file_replicas.append(pfn_file_replica)
            attached_dids.append(AttachedFile(did=pfn_file_replica.did, size=pfn_file_replica.size))

        did = scope + ':' + name
        self.db.set_attached_files(self.namespace, did, attached_dids)

        return pfn_file_replicas

    def fetch_file_replicas(self, scope, name):
        destination_rse = self.rucio.instance_config.get('destination_rse')

        replicas = []
        rucio_replicas = self.rucio.get_replicas(scope, name)

        def rucio_replica_mapper(rucio_replica, _):
            rses = rucio_replica['rses']
            scope = rucio_replica['scope']
            name = rucio_replica['name']
            size = rucio_replica['bytes']
            states = rucio_replica.get('states')    # If there is no replica, states is omitted

            pfn = None
            if (states is not None) and (destination_rse in rses) and (destination_rse in states):
                if states[destination_rse] == 'AVAILABLE':
                    pfns = rses[destination_rse]
                    if len(pfns) > 0:
                        pfn = pfns[0]

            did = scope + ':' + name
            return PfnFileReplica(pfn=pfn, did=did, size=size)

        replicas = utils.map(rucio_replicas, rucio_replica_mapper)
        return replicas

    def get_did_status(self, scope, name):
        status = ReplicaModeHandler.STATUS_NOT_AVAILABLE
        replication_rule = self.fetch_replication_rule_by_did(scope, name)
        if replication_rule is not None:
            _, replication_status, _ = replication_rule
            status = replication_status

        return status

    def fetch_replication_rule_by_did(self, scope, name):
        destination_rse = self.rucio.instance_config.get('destination_rse')

        rules = self.rucio.get_rules(scope, name)
        filtered_rules = utils.filter(rules, lambda x, _: x['rse_expression'] == destination_rse)

        if len(filtered_rules) > 0:
            replication_rule = filtered_rules[0]
            rule_id = replication_rule.get('id')
            status = self.parse_rule_status(replication_rule.get('state'))
            expires_at = replication_rule.get('expires_at')

            return (rule_id, status, expires_at)

        return None

    def parse_rule_status(self, status):
        if status == 'OK':
            status = ReplicaModeHandler.STATUS_OK
        elif status == 'REPLICATING':
            status = ReplicaModeHandler.STATUS_REPLICATING
        else:
            status = ReplicaModeHandler.STATUS_STUCK

        return status

    def translate_pfn_to_path(self, pfn):
        instance_config = self.rucio.instance_config
        prefix_path = instance_config.get('rse_mount_path')
        path_begins_at = instance_config.get('path_begins_at', 0)

        path = urlparse(pfn).path
        suffix_path = self.get_path_after_nth_slash(path, path_begins_at)
        return os.path.join(prefix_path, suffix_path)

    def get_path_after_nth_slash(self, path, nth_slash):
        return path.strip('/').split('/', nth_slash)[-1]
