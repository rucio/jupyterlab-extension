# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json
import tornado
import rucio_jupyterlab.utils as utils
from .base import RucioAPIHandler


class OpenReplicationRuleHandler(RucioAPIHandler):
    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        did = self.get_query_argument('did')
        scope, name = did.split(':')

        rucio_instance = self.rucio.for_instance(namespace)
        mode = rucio_instance.instance_config.get('mode', 'replica')
        rucio_webui_url = rucio_instance.instance_config.get('rucio_webui_url')

        if not rucio_webui_url:
            self.set_status(500)
            self.finish("Rucio WebUI URL is not configured")
            return

        if mode != 'replica':
            self.set_status(400)
            self.finish("Extension is not in Replica mode")
            return

        replication_rule = self._resolve_did_replication_rule(rucio_instance, scope, name)
        if not replication_rule:
            self.set_status(404)
            self.finish('DID has no replication rule')
            return

        rule_id, _ = replication_rule

        url = f"{rucio_webui_url}/rule?rule_id={rule_id}"
        self.redirect(url)

    def _resolve_did_replication_rule(self, rucio_instance, scope, name):
        replication_rule = self._fetch_replication_rule(rucio_instance, scope, name)

        if replication_rule is not None:
            return replication_rule

        parents = rucio_instance.get_parents(scope, name)
        if len(parents) == 0:
            return None

        for parent in parents:
            replication_rule = self._fetch_replication_rule(rucio_instance, scope=parent['scope'], name=parent['name'])
            if replication_rule is not None:
                return replication_rule

        return None

    def _fetch_replication_rule(self, rucio_instance, scope, name):
        destination_rse = rucio_instance.instance_config.get('destination_rse')

        rules = rucio_instance.get_rules(scope, name)
        filtered_rules = utils.filter(rules, lambda x, _: x['rse_expression'] == destination_rse)

        if len(filtered_rules) > 0:
            replication_rule = filtered_rules[0]
            rule_id = replication_rule.get('id')
            expires_at = replication_rule.get('expires_at')

            return rule_id, expires_at

        return None
