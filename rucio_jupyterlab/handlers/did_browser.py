# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025

import json
import logging
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile
from rucio_jupyterlab.rucio.authenticators import RucioAuthenticationException
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics
import tornado

# Configure logging
logger = logging.getLogger(__name__)


class DIDBrowserHandlerImpl:
    """
    Implementation of a handler for browsing Data Identifier (DID) files.

    This class provides functionality to fetch files associated with a given DID
    (Data Identifier) either from a local cache or directly from Rucio.

    Attributes:
        namespace (str): The namespace associated with the handler.
        rucio (object): An instance of the Rucio client used for interacting with Rucio.
        db (object): A database instance used for caching attached files.

    Methods:
        __init__(namespace, rucio):
            Initializes the DIDBrowserHandlerImpl instance with the given namespace and Rucio client.

        get_files(scope, name, force_fetch=False):
            Fetches files associated with the given DID (scope:name). Files are retrieved
            from the local cache if available, or fetched directly from Rucio if `force_fetch`
            is set to True or no cached files are found.
    """

    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name
        logger.info("DIDBrowserHandlerImpl initialized with namespace: %s", namespace)
        logger.debug("Namespace: %s, Rucio instance: %s", namespace, rucio)

    def get_files(self, scope, name, force_fetch=False):
        parent_did = f'{scope}:{name}'
        logger.info("Fetching files for DID: %s, force_fetch=%s", parent_did, force_fetch)
        logger.debug("Scope: %s, Name: %s, Force fetch: %s", scope, name, force_fetch)

        attached_files = self.db.get_attached_files(namespace=self.namespace, did=parent_did) if not force_fetch else None
        if attached_files:
            logger.info("Found cached attached files for DID: %s", parent_did)
            logger.debug("Cached attached files: %s", attached_files)
            return [d.__dict__ for d in attached_files]

        logger.info("No cached files found for DID: %s. Fetching from Rucio.", parent_did)
        file_dids = self.rucio.get_replicas(scope, name)
        logger.debug("Fetched file DIDs from Rucio: %s", file_dids)
        attached_files = [AttachedFile(did=(d.get('scope') + ':' + d.get('name')), size=d.get('bytes')) for d in file_dids]
        self.db.set_attached_files(self.namespace, parent_did, attached_files)
        logger.info("Fetched and cached %d files for DID: %s", len(attached_files), parent_did)
        logger.debug("Attached files cached: %s", attached_files)
        return [d.__dict__ for d in attached_files]


class DIDBrowserHandler(RucioAPIHandler):
    """
    A Tornado web handler for browsing Data Identifier (DID) files in Rucio.

    This handler processes GET requests to retrieve files associated with a specific DID
    within a given namespace. It supports polling functionality and handles authentication
    errors gracefully.

    Methods:
        get():
            Handles GET requests to fetch files for a specified DID. The method expects
            the following query arguments:
                - namespace: The Rucio namespace to operate within.
                - poll: A flag indicating whether polling is enabled (default is '0').
                - did: The Data Identifier in the format 'scope:name'.

            The method interacts with the Rucio API to fetch files and returns the results
            as a JSON response. If authentication fails, it responds with a 401 status code
            and an error message.

    Raises:
        RucioAuthenticationException: If authentication with the Rucio API fails.
    """
    @tornado.web.authenticated
    @prometheus_metrics
    def get(self):
        namespace = self.get_query_argument('namespace')
        poll = self.get_query_argument('poll', '0') == '1'
        did = self.get_query_argument('did')
        logger.info("Handling GET request for namespace: %s, DID: %s, poll=%s", namespace, did, poll)
        logger.debug("Query arguments - Namespace: %s, Poll: %s, DID: %s", namespace, poll, did)

        rucio = self.rucio.for_instance(namespace)
        (scope, name) = did.split(':')
        logger.debug("Split DID into scope: %s, name: %s", scope, name)

        handler = DIDBrowserHandlerImpl(namespace, rucio)

        try:
            dids = handler.get_files(scope, name, poll)
            logger.info("Successfully fetched files for DID: %s", did)
            logger.debug("Fetched files: %s", dids)
            self.finish(json.dumps(dids))
        except RucioAuthenticationException:
            logger.error("Authentication error while fetching files for DID: %s", did)
            self.set_status(401)
            self.finish(json.dumps({'error': 'Authentication error '}))
        except Exception as e:
            logger.error("An error occurred while fetching files for DID: %s. Error: %s", did, str(e))
            self.set_status(500)
            self.finish(json.dumps({'error': 'Internal server error', 'message': str(e)}))
