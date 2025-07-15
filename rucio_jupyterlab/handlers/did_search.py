# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Alba Vendrell, (CERN), 2022
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import json
import logging
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.rucio.exceptions import RucioAPIException
import rucio_jupyterlab.utils as utils
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics
import tornado

ROW_LIMIT = 1000

# Setup logging
logger = logging.getLogger(__name__)


class WildcardDisallowedException(BaseException):
    pass


class DIDSearchHandlerImpl:
    def __init__(self, namespace, rucio):
        """
        Initialize the DIDSearchHandlerImpl with the given namespace and rucio instance.
        :param namespace: The namespace for the Rucio instance.
        :param rucio: The Rucio instance to interact with.
        """

        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name
        logger.info("DIDSearchHandlerImpl initialized for namespace: %s", namespace)

    def search_did(self, scope, name, search_type, filters, limit):
        logger.info("Searching DID with scope: %s, name: %s, type: %s, filters: %s, limit: %s", scope, name, search_type, filters, limit)
        wildcard_enabled = self.rucio.instance_config.get('wildcard_enabled', False)

        if ('*' in name or '%' in name) and not wildcard_enabled:
            logger.warning("Wildcard search attempted but is disabled in the configuration.")
            raise WildcardDisallowedException()
        dids = self.rucio.search_did(scope, name, search_type, filters, limit)
        logger.debug("Initial search results: %s", dids)

        # Check if filters are provided and if dids are found
        if filters and not dids:
            print(filters)
            # If no filters are provided and no DIDs are found, search for all DIDs in the scope
            raise ValueError("No DIDs found for scope: \"%s\" and filters: %s. Please check the parameters or try a different search." % (scope, filters))
        # If filters are provided but no DIDs are found, raise an error
        if not filters and not dids:
            raise ValueError("No DIDs found for scope: \"%s\". Please check the parameters or try a different search." % (scope))

        try:
            for did in dids:
                if did['did_type'] is None:  # JSON plugin was used lacking data
                    logger.debug("Fetching metadata for DID with scope: %s, name: %s", scope, did['name'])
                    metadata_str = self.rucio.get_metadata(scope, did['name']) # This should be a single dict
                    metadata = json.loads(metadata_str) # Convert JSON string to dict

                    did['did_type'] = metadata['did_type']
                    did['bytes'] = metadata['bytes']
                    did['length'] = metadata['length']
                    logger.debug("Updated DID metadata: %s", did)
        except Exception as e:
            logger.error(e)
            self.set_status(500)
            self.finish(json.dumps({
                'success': False,
                'error': str(e)
            }))

        def mapper(entry, _):
            logger.debug("Mapping entry: %s", entry)
            did_type = entry.get('did_type')
            type_str = ''
            if isinstance(did_type, str):
                if '.' in did_type:
                    type_str = did_type.split('.', 1)[-1].lower()
                    logger.warning("DIDType.* is a deprecated format, please upgrade Rucio Servers to v35+ to have the format without DIDType prefix.")
                else:
                    type_str = did_type.lower()
            else:
                logger.warning("Unexpected did_type format: %r", did_type)
            return {
                'did': f"{entry.get('scope')}:{entry.get('name')}",
                'size': entry.get('bytes'),
                'type': type_str
            }

        result = utils.map(dids, mapper)
        logger.info("Search result processed: %s", result)
        return result


class DIDSearchHandler(RucioAPIHandler):
    @tornado.web.authenticated
    @prometheus_metrics
    def get(self):
        namespace = self.get_query_argument('namespace')
        search_type = self.get_query_argument('type', 'collection')
        did = self.get_query_argument('did')
        filters = self.get_query_argument('filters', default=None)
        logger.info("Received DID search request: namespace=%s, type=%s, did=%s, filters=%s", namespace, search_type, did, filters)
        rucio = self.rucio.for_instance(namespace)

        try:
            (scope, name) = did.split(':')
            if not scope or not name:
                raise ValueError()
        except ValueError as e:
            logger.error("Malformed DID received: '%s'. Expected format: scope:name", did)
            self.set_status(400)
            self.finish(json.dumps({
                'success': False,
                'error': str(f"Malformed DID received: '{did}'. Expected format: scope:name")
            }))
            return
        handler = DIDSearchHandlerImpl(namespace, rucio)

        try:
            dids = handler.search_did(scope, name, search_type, filters, ROW_LIMIT)
            logger.info("DID search successful. Returning %d results.", len(dids))
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
        except ValueError as e:
            logger.warning(e)
            self.set_status(404)
            self.finish(json.dumps({
                'success': False,
                'error': str(e)
            }))
