# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Alba Vendrell, (CERN), 2022

import json
import logging
import tornado
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.rucio.exceptions import RucioAPIException
import rucio_jupyterlab.utils as utils
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics

ROW_LIMIT = 1000

# Setup logging
logger = logging.getLogger(__name__)

class WildcardDisallowedException(BaseException):
    pass


class DIDSearchHandlerImpl:
    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name
        logger.info(f"DIDSearchHandlerImpl initialized for namespace: {namespace}")

    def search_did(self, scope, name, search_type, filters, limit):
        logger.info(f"Searching DID with scope: {scope}, name: {name}, type: {search_type}, filters: {filters}, limit: {limit}")
        wildcard_enabled = self.rucio.instance_config.get('wildcard_enabled', False)

        if ('*' in name or '%' in name) and not wildcard_enabled:
            logger.warning("Wildcard search attempted but is disabled in the configuration.")
            raise WildcardDisallowedException()

        dids = self.rucio.search_did(scope, name, search_type, filters, limit)
        logger.debug(f"Initial search results: {dids}")

        for did in dids:
            if did['did_type'] is None:  # JSON plugin was used lacking data
                logger.debug(f"Fetching metadata for DID with scope: {scope}, name: {did['name']}")
                metadata = self.rucio.get_metadata(scope, did['name'])[0]
                did['did_type'] = f"DIDType.{metadata['did_type']}"
                did['bytes'] = metadata['bytes']
                did['length'] = metadata['length']
                logger.debug(f"Updated DID metadata: {did}")

        def mapper(entry, _):
            logger.debug(f"Mapping entry: {entry}")
            return {
                'did': entry.get('scope') + ':' + entry.get('name'),
                'size': entry.get('bytes'),
                'type': (entry.get('did_type').lower()).split(".")[1]
            }

        result = utils.map(dids, mapper)
        logger.info(f"Search result processed: {result}")
        return result


class DIDSearchHandler(RucioAPIHandler):
    @tornado.web.authenticated
    @prometheus_metrics
    def get(self):
        namespace = self.get_query_argument('namespace')
        search_type = self.get_query_argument('type', 'collection')
        did = self.get_query_argument('did')
        filters = self.get_query_argument('filters', default=None)
        logger.info(f"Received DID search request: namespace={namespace}, type={search_type}, did={did}, filters={filters}")
        rucio = self.rucio.for_instance(namespace)

        (scope, name) = did.split(':')
        handler = DIDSearchHandlerImpl(namespace, rucio)

        try:
            dids = handler.search_did(scope, name, search_type, filters, ROW_LIMIT)
            logger.info(f"DID search successful. Returning {len(dids)} results.")
            self.finish(json.dumps(dids))
        except WildcardDisallowedException:
            logger.warning("Wildcard search is disabled and was attempted.")
            self.set_status(400)
            self.finish(json.dumps({'error': 'wildcard_disabled'}))
        except RucioAPIException as e:
            # Set the HTTP status from the exception, falling back to 500 if not present
            self.set_status(e.status_code or 500)
            
            # Finish the request with a detailed JSON error payload
            self.finish(json.dumps({
                'success': False,
                'error': e.message,
                'exception_class': e.exception_class,
                'exception_message': e.exception_message
            }))
