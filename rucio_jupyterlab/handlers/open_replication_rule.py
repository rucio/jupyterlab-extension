# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import html
import logging
import tornado
import rucio_jupyterlab.utils as utils
from .base import RucioHandler

logger = logging.getLogger(__name__)

# HTML template for 404 page
template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Rule Not Found - Rucio JupyterLab Extension</title>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">
  <style type="text/css">
  .content {
    max-width: 600px;
    margin: 0 auto;
    padding: 16px;
    margin-top: 24px;
  }
  .button {
    margin-top: 8px;
  }
  </style>
</head>
<body>
    <div class="content">
      <!-- SVG and content omitted for brevity -->
      <h3>DID has no related replication rule</h3>
      <p>There is no replication rule belonging to the DID <code>{{ did }}</code> or the parent DIDs on RSE <code>{{ rse_name }}</code></p>
      <a href="{{ did_page_url }}">
        <button type="button" class="btn btn-primary button">View DID on Rucio WebUI</button>
      </a>
    </div>
</body>
</html>
"""


def render_rule_not_found_html(**kwargs):
    rendered = template
    for key, value in kwargs.items():
        rendered = rendered.replace("{{ " + key + " }}", html.escape(str(value)))
    return rendered


class OpenReplicationRuleHandler(RucioHandler):
    """
    Handler to open the replication rule page for a given Data Identifier (DID).
    This handler processes requests to retrieve the replication rule associated with a DID,
    including its parent DIDs if necessary. If no rule is found, it renders a 404 page.
    """
    @tornado.web.authenticated
    def get(self):
        try:
            namespace = self.get_query_argument('namespace')
            did = self.get_query_argument('did')
            logger.info("Received request for DID '%s' in namespace '%s'.", did, namespace)

            if ':' not in did:
                logger.warning("Malformed DID received: '%s'", did)
                self.set_status(400)
                self.finish("Malformed DID. Expected format: scope:name")
                return

            scope, name = did.split(':', 1)

            try:
                rucio_instance = self.rucio.for_instance(namespace)
            except Exception as e:
                logger.error("Failed to get Rucio instance for namespace '%s': %s", namespace, e, exc_info=True)
                self.set_status(500)
                self.finish("Internal server error: could not retrieve Rucio instance.")
                return

            mode = rucio_instance.instance_config.get('mode', 'replica')
            rucio_webui_url = rucio_instance.instance_config.get('rucio_webui_url')

            if not rucio_webui_url:
                logger.error("Rucio WebUI URL is not configured in the instance config.")
                self.set_status(500)
                self.finish("Rucio WebUI URL is not configured")
                return

            if mode != 'replica':
                logger.warning("Extension is not in Replica mode (mode=%s).", mode)
                self.set_status(400)
                self.finish("Extension is not in Replica mode")
                return

            try:
                replication_rule = self._resolve_did_replication_rule(rucio_instance, scope, name)
            except Exception as e:
                logger.error("Failed to resolve replication rule for DID '%s': %s", did, e, exc_info=True)
                self.set_status(500)
                self.finish("Internal server error while resolving replication rule.")
                return

            if not replication_rule:
                logger.info("No replication rule found for DID '%s' or its parents.", did)
                did_page_url = f"{rucio_webui_url}/did?scope={scope}&name={name}"
                destination_rse = rucio_instance.instance_config.get('destination_rse', 'N/A')
                self.set_status(404)
                self.finish(render_rule_not_found_html(
                    rse_name=destination_rse,
                    did=f"{scope}:{name}",
                    did_page_url=did_page_url
                ))
                return

            rule_id, _ = replication_rule
            url = f"{rucio_webui_url}/rule?rule_id={rule_id}"
            logger.info("Redirecting to replication rule page: %s", url)
            self.redirect(url)

        except Exception as e:
            logger.critical("Unhandled exception in OpenReplicationRuleHandler: %s", e, exc_info=True)
            self.set_status(500)
            self.finish("Internal server error.")

    def _resolve_did_replication_rule(self, rucio_instance, scope, name):
        # Try direct rule
        replication_rule = self._fetch_replication_rule(rucio_instance, scope, name)
        if replication_rule:
            logger.debug("Found replication rule for DID '%s:%s'.", scope, name)
            return replication_rule

        # Try parent DIDs
        try:
            parents = rucio_instance.get_parents(scope, name)
        except Exception as e:
            logger.error("Error fetching parents for DID '%s:%s': %s", scope, name, e, exc_info=True)
            return None

        if not parents:
            logger.debug("No parents found for DID '%s:%s'.", scope, name)
            return None

        for parent in parents:
            parent_scope = parent.get('scope')
            parent_name = parent.get('name')
            if not parent_scope or not parent_name:
                logger.warning("Malformed parent entry: %s", parent)
                continue
            replication_rule = self._fetch_replication_rule(rucio_instance, scope=parent_scope, name=parent_name)
            if replication_rule:
                logger.debug("Found replication rule for parent DID '%s:%s'.", parent_scope, parent_name)
                return replication_rule

        logger.debug("No replication rule found for DID '%s:%s' or any parents.", scope, name)
        return None

    def _fetch_replication_rule(self, rucio_instance, scope, name):
        try:
            destination_rse = rucio_instance.instance_config.get('destination_rse')
            rules = rucio_instance.get_rules(scope, name)
            filtered_rules = utils.filter(rules, lambda x, _: x.get('rse_expression') == destination_rse)
            if filtered_rules:
                replication_rule = filtered_rules[0]
                rule_id = replication_rule.get('id')
                expires_at = replication_rule.get('expires_at')
                logger.debug("Replication rule found for '%s:%s', rule_id=%s.", scope, name, rule_id)
                return rule_id, expires_at
            else:
                logger.debug("No matching replication rules for '%s:%s' on RSE '%s'.", scope, name, destination_rse)
                return None
        except Exception as e:
            logger.error("Error fetching rules for DID '%s:%s': %s", scope, name, e, exc_info=True)
            return None
