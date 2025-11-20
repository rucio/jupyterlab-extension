import os
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict
from urllib.parse import urlparse
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile, PfnFileReplica
from rucio_jupyterlab import utils

logger = logging.getLogger(__name__)


class ReplicaModeHandler:
    """
    Handles replica-related operations, including fetching, status, and replication.
    """
    STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
    STATUS_REPLICATING = "REPLICATING"
    STATUS_FETCHING = "FETCHING"
    STATUS_OK = "OK"
    STATUS_STUCK = "STUCK"

    # Class-level shared state for tracking inflight fetches across all instances
    _inflight_lock = threading.Lock()
    _inflight_fetches: Dict[str, Future] = {}
    _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="rucio_fetcher")

    def __init__(self, namespace, rucio):
        """
        Initializes the ReplicaModeHandler.

        Args:
            namespace (str): The namespace for database operations.
            rucio (RucioAPI): An instance of the Rucio API client.
        """
        self.namespace = namespace
        self.rucio = rucio
        self.db = get_db()  # pylint: disable=invalid-name
        # Thread pool for async DB writes (instance-specific)
        self._write_lock = threading.Lock()
        logger.info("ReplicaModeHandler initialized for namespace: %s", self.namespace)

    def make_available(self, scope, name):
        """
        Initiates a replication rule to make a DID available.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.

        Returns:
            Any: The result from the Rucio API call.
        """
        logger.info("Attempting to make DID '%s:%s' available.", scope, name)
        dids = [{'scope': scope, 'name': name}]
        destination_rse = self.rucio.instance_config.get('destination_rse')
        lifetime_days = self.rucio.instance_config.get('replication_rule_lifetime_days')
        lifetime = (lifetime_days * 60 * 60 * 24) if lifetime_days else None

        logger.debug("Replication parameters: destination_rse='%s', lifetime_days=%s (calculated lifetime=%s)", destination_rse, lifetime_days, lifetime)

        try:
            replication_result = self.rucio.add_replication_rule(dids=dids, rse_expression=destination_rse, copies=1, lifetime=lifetime)
            logger.info("Successfully initiated replication rule for '%s:%s'. Result: %s", scope, name, replication_result)
            return replication_result
        except Exception as e:
            logger.error("Failed to add replication rule for '%s:%s'. Error: %s", scope, name, e, exc_info=True)
            raise  # Re-raise the exception after logging

    def get_did_details(self, scope, name, force_fetch=False):
        """
        Retrieves details for a DID, including its replication status and path.
        Returns immediately with cached data or placeholder data while fetching in background.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.
            force_fetch (bool): If True, forces fetching from Rucio instead of DB.

        Returns:
            list[dict]: A list of dictionaries, each containing status, DID, path, size, and PFN.
        """
        logger.info("Getting DID details for '%s:%s', force_fetch=%s.", scope, name, force_fetch)
        did = scope + ':' + name
        
        # Check if there's an ongoing fetch for this DID
        with self._inflight_lock:
            ongoing_fetch = self._inflight_fetches.get(did)
            is_fetching = ongoing_fetch is not None and not ongoing_fetch.done()
        
        logger.debug("DID '%s': is_fetching=%s, force_fetch=%s", did, is_fetching, force_fetch)
        
        # Try to get cached data first
        attached_file_replicas = self.get_attached_file_replicas(scope, name, force_fetch)
        
        logger.debug("DID '%s': got %d attached_file_replicas from cache/db", did, len(attached_file_replicas) if attached_file_replicas else 0)
        
        # If no cached data
        if not attached_file_replicas:
            if is_fetching:
                # Fetch is already in progress, return FETCHING status
                logger.info("Fetch in progress for '%s:%s'. Returning FETCHING status.", scope, name)
                return [{
                    'status': ReplicaModeHandler.STATUS_FETCHING,
                    'did': did,
                    'path': None,
                    'size': 0,
                    'pfn': None,
                    'message': 'Fetching replica information...',
                    'progress': {'mode': 'indeterminate'}
                }]
            elif not force_fetch:
                # No cache and no ongoing fetch, start one
                logger.info("No cached data for '%s:%s'. Returning placeholder and fetching async.", scope, name)
                
                # Trigger async fetch
                self._fetch_and_cache_async(scope, name, did)
                
                # Return placeholder indicating data is being fetched
                return [{
                    'status': ReplicaModeHandler.STATUS_FETCHING,
                    'did': did,
                    'path': None,
                    'size': 0,
                    'pfn': None,
                    'message': 'Fetching replica information...',
                    'progress': {'mode': 'indeterminate'}
                }]
            # If force_fetch and no data, fall through to sync fetch (which shouldn't happen normally)
            logger.warning("Force fetch requested for '%s:%s' but no data found. This is unexpected.", scope, name)
        
        # We have some cached data - check if it's complete
        complete = utils.find(lambda x: x.pfn is None, attached_file_replicas) is None
        logger.debug("Attached file replicas retrieved. Count: %d. All PFNs present (complete): %s", len(attached_file_replicas), complete)

        status = ReplicaModeHandler.STATUS_NOT_AVAILABLE
        if not complete:
            logger.debug("PNFs are not complete, determining DID status from replication rule.")
            status = self.get_did_status(scope, name)
            logger.debug("Determined DID status: %s", status)
        else:
            logger.debug("All PFNs are complete, assuming OK status for individual files unless otherwise specified.")

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
        logger.info("Finished getting DID details for '%s:%s'. Returned %d results.", scope, name, len(results))
        return results

    def _fetch_and_cache_async(self, scope, name, did):
        """
        Fetches replicas asynchronously and caches them without blocking.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.
            did (str): The full DID string.
        """
        def _fetch():
            try:
                logger.debug("Async fetch started for '%s'.", did)
                fetched_file_replicas = self.fetch_file_replicas(scope, name)

                if fetched_file_replicas:
                    self._cache_replicas(did, fetched_file_replicas)
                    logger.info("Async fetch completed for '%s': cached %d replicas.", did, len(fetched_file_replicas))
                else:
                    logger.debug("Async fetch for '%s': no replicas found.", did)
            except Exception as e:
                logger.error("Async fetch failed for '%s': %s", did, e, exc_info=True)

        self._schedule_fetch_task(did, _fetch, "initial_fetch")

    def get_attached_file_replicas(self, scope, name, force_fetch=False):
        """
        Gets attached file replicas, either from the database or by fetching from Rucio.
        Implements optimistic caching: returns stale data immediately while refreshing in background.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.
            force_fetch (bool): If True, forces fetching from Rucio (synchronously).

        Returns:
            list[PfnFileReplica]: A list of PfnFileReplica objects, or empty list if no cache.
        """
        logger.info("Getting attached file replicas for '%s:%s', force_fetch=%s.", scope, name, force_fetch)
        did = scope + ':' + name
        attached_files = None
        fetch_reason = None
        
        if not force_fetch:
            attached_files = self.db.get_attached_files(self.namespace, did)
            if attached_files:
                logger.debug("Found %d attached files in DB for '%s'.", len(attached_files), did)
            else:
                logger.debug("No attached files found in DB for '%s'.", did)
                # Return empty list - caller will handle async fetch
                return []
        else:
            fetch_reason = "force_fetch_true"

        pfn_file_replicas = None
        if attached_files:
            pfn_file_replicas = self.get_all_pfn_file_replicas_from_db(attached_files)
            if pfn_file_replicas:
                logger.debug("Successfully retrieved PFN file replicas from DB for '%s'. Count: %d", did, len(pfn_file_replicas))
                
                # Optimistic refresh: return cached data immediately, refresh in background
                if not force_fetch:
                    self._refresh_replicas_async(scope, name, did)
                
                return pfn_file_replicas
            else:
                logger.debug("Failed to retrieve all PFN file replicas from DB for '%s'. Will fetch.", did)
                fetch_reason = "partial_replica_cache"

        # Only perform synchronous fetch if force_fetch=True
        if force_fetch:
            if fetch_reason is None:
                fetch_reason = "unknown_cache_miss"
            logger.info("Force fetch (%s). Fetching attached PFN file replicas from Rucio for '%s'.", fetch_reason, did)
            pfn_file_replicas = self.fetch_attached_pfn_file_replicas(scope, name)
            logger.debug("Fetched %d PFN file replicas from Rucio for '%s'.", len(pfn_file_replicas), did)
            return pfn_file_replicas
        
        # No cache and not force_fetch - return empty, let caller decide
        logger.info("No cached replicas for '%s' and not forcing fetch. Returning empty list.", did)
        return []

    def fetch_attached_pfn_file_replicas(self, scope, name):
        """
        Fetches PFN file replicas from Rucio and stores them in the database.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.

        Returns:
            list[PfnFileReplica]: A list of fetched PfnFileReplica objects.
        """
        logger.info("Fetching and storing attached PFN file replicas for '%s:%s' from Rucio.", scope, name)
        fetched_file_replicas = self.fetch_file_replicas(scope, name)
        logger.debug("Rucio returned %d file replicas for '%s:%s'.", len(fetched_file_replicas), scope, name)

        if not fetched_file_replicas:
            logger.info("No file replicas returned for '%s:%s'. Nothing to cache.", scope, name)
            return []

        did = scope + ':' + name
        self._cache_replicas(did, fetched_file_replicas)
        logger.info("Stored %d attached DIDs for '%s' in DB.", len(fetched_file_replicas), did)

        logger.debug("Returning %d fetched PFN file replicas.", len(fetched_file_replicas))
        return fetched_file_replicas

    def _refresh_replicas_async(self, scope, name, did):
        """
        Refreshes replicas in the background without blocking the current request.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.
            did (str): The full DID string.
        """
        def _refresh():
            try:
                logger.debug("Background refresh started for '%s'.", did)
                fetched_file_replicas = self.fetch_file_replicas(scope, name)

                if fetched_file_replicas:
                    self._cache_replicas(did, fetched_file_replicas)
                    logger.info("Background refresh completed for '%s': updated %d replicas.", did, len(fetched_file_replicas))
                else:
                    logger.debug("Background refresh for '%s': no replicas to update.", did)
            except Exception as e:
                logger.error("Background refresh failed for '%s': %s", did, e, exc_info=True)

        self._schedule_fetch_task(did, _refresh, "background_refresh")

    def get_all_pfn_file_replicas_from_db(self, attached_files):
        """
        Retrieves all PFN file replicas from the database based on a list of attached files.
        Uses bulk query to avoid N+1 problem with large datasets.

        Args:
            attached_files (list[AttachedFile]): A list of AttachedFile objects.

        Returns:
            list[PfnFileReplica] or None: A list of PfnFileReplica objects if all found, else None.
        """
        import time
        start_time = time.time()
        count = len(attached_files)
        logger.debug("Retrieving %d PFN file replicas from DB.", count)
        
        # Extract all DIDs and use bulk query
        file_dids = [af.did for af in attached_files]
        replica_dict = self.db.get_file_replicas_bulk(self.namespace, file_dids)
        
        if replica_dict is None:
            logger.warning("Incomplete cache - some replicas not found in DB.")
            return None
        
        # Build result list in same order as input
        pfn_file_replicas = []
        for attached_file in attached_files:
            db_file_replica = replica_dict.get(attached_file.did)
            if db_file_replica is None:
                # This shouldn't happen given the check above, but be defensive
                logger.warning("File replica for '%s' not in bulk result.", attached_file.did)
                return None
            
            pfn_file_replica = PfnFileReplica(
                did=db_file_replica.did, 
                pfn=db_file_replica.pfn, 
                size=db_file_replica.size
            )
            pfn_file_replicas.append(pfn_file_replica)

        duration = time.time() - start_time
        logger.info("Retrieved %d PFN file replicas from DB in %.2fs (%.0f replicas/sec)", 
                   count, duration, count/duration if duration > 0 else 0)
        return pfn_file_replicas

    def fetch_file_replicas(self, scope, name):
        """
        Fetches file replicas for a given DID from Rucio.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.

        Returns:
            list[PfnFileReplica]: A list of PfnFileReplica objects.
        """
        import time
        start_time = time.time()
        logger.info("Fetching file replicas from Rucio for '%s:%s'.", scope, name)
        destination_rse = self.rucio.instance_config.get('destination_rse')

        replicas = []
        try:
            rucio_replicas = self.rucio.get_replicas(scope, name)
            fetch_duration = time.time() - start_time
            logger.info("Rucio returned %d raw replicas for '%s:%s' in %.2fs.", 
                       len(rucio_replicas), scope, name, fetch_duration)
        except Exception as e:
            logger.error("Failed to fetch replicas from Rucio for '%s:%s'. Error: %s", scope, name, e, exc_info=True)
            return []  # Return empty list on error

        # Track statistics to avoid thousands of log lines
        stats = {'available': 0, 'unavailable': 0, 'no_pfn': 0}
        
        def rucio_replica_mapper(rucio_replica, _):
            rses = rucio_replica.get('rses', {})
            scope = rucio_replica.get('scope')
            name = rucio_replica.get('name')
            size = rucio_replica.get('bytes')
            states = rucio_replica.get('states')    # If there is no replica, states is omitted

            pfn = None
            if destination_rse in rses and destination_rse in states:
                if states[destination_rse] == 'AVAILABLE':
                    pfns = rses[destination_rse]
                    if pfns:
                        pfn = pfns[0]
                        stats['available'] += 1
                    else:
                        stats['no_pfn'] += 1
                else:
                    stats['unavailable'] += 1
            else:
                stats['unavailable'] += 1

            did = scope + ':' + name
            return PfnFileReplica(pfn=pfn, did=did, size=size)

        replicas = utils.map(rucio_replicas, rucio_replica_mapper)
        total_duration = time.time() - start_time
        logger.info("Processed %d replicas for '%s:%s' in %.2fs: %d available, %d unavailable, %d missing PFN", 
                   len(replicas), scope, name, total_duration, 
                   stats['available'], stats['unavailable'], stats['no_pfn'])
        return replicas

    def get_did_status(self, scope, name):
        """
        Determines the replication status of a DID.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.

        Returns:
            str: The status (e.g., STATUS_NOT_AVAILABLE, STATUS_REPLICATING, STATUS_OK, STATUS_STUCK).
        """
        logger.info("Getting DID status for '%s:%s'.", scope, name)
        status = ReplicaModeHandler.STATUS_NOT_AVAILABLE
        replication_rule = self.fetch_replication_rule_by_did(scope, name)
        if replication_rule is not None:
            _, replication_status, _ = replication_rule
            status = replication_status
            logger.debug("Replication rule found, status: '%s'.", status)
        else:
            logger.debug("No replication rule found for '%s:%s'. Status remains '%s'.", scope, name, status)

        logger.info("Determined DID status for '%s:%s': %s.", scope, name, status)
        return status

    def fetch_replication_rule_by_did(self, scope, name):
        """
        Fetches the replication rule for a DID by ID.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.

        Returns:
            tuple or None: (rule_id, status, expires_at) or None if no rule found.
        """
        logger.info("Fetching replication rule for DID '%s:%s'.", scope, name)
        destination_rse = self.rucio.instance_config.get('destination_rse')
        logger.debug("Filtering rules for destination RSE: '%s'.", destination_rse)

        try:
            rules = self.rucio.get_rules(scope, name)
            logger.debug("Rucio returned %d rules for '%s:%s'.", len(rules), scope, name)
        except Exception as e:
            logger.error("Failed to fetch rules from Rucio for '%s:%s'. Error: %s", scope, name, e, exc_info=True)
            return None  # Return None on error

        filtered_rules = utils.filter(rules, lambda x, _: x['rse_expression'] == destination_rse)

        if filtered_rules:
            replication_rule = filtered_rules[0]
            rule_id = replication_rule.get('id')
            parsed_status = self.parse_rule_status(replication_rule.get('state'))
            expires_at = replication_rule.get('expires_at')
            logger.info("Found replication rule for '%s:%s': ID=%s, Status='%s', Expires='%s'.", scope, name, rule_id, parsed_status, expires_at)
            return (rule_id, parsed_status, expires_at)
        else:
            logger.info("No replication rule found for '%s:%s' matching destination RSE '%s'.", scope, name, destination_rse)
            return None

    def parse_rule_status(self, status):
        """
        Parses a Rucio rule status string into a standardized ReplicaModeHandler status.

        Args:
            status (str): The raw Rucio rule status.

        Returns:
            str: The parsed status.
        """
        logger.debug("Parsing Rucio rule status: '%s'.", status)
        if status == 'OK':
            parsed_status = ReplicaModeHandler.STATUS_OK
        elif status == 'REPLICATING':
            parsed_status = ReplicaModeHandler.STATUS_REPLICATING
        else:
            parsed_status = ReplicaModeHandler.STATUS_STUCK
            logger.warning("Unknown Rucio rule status '%s' parsed as '%s'.", status, parsed_status)
        logger.debug("Parsed status: '%s'.", parsed_status)
        return parsed_status

    def translate_pfn_to_path(self, pfn):
        """
        Translates a PFN (Physical File Name) to a local file path.

        Args:
            pfn (str): The PFN to translate.

        Returns:
            str: The translated local file path.
        """
        instance_config = self.rucio.instance_config
        prefix_path = instance_config.get('rse_mount_path')
        path_begins_at = instance_config.get('path_begins_at', 0)

        path = urlparse(pfn).path
        suffix_path = self.get_path_after_nth_slash(path, path_begins_at)

        full_path = os.path.join(prefix_path, suffix_path)
        return full_path

    def get_path_after_nth_slash(self, path, nth_slash):
        """
        Extracts the part of a path after the nth slash.

        Args:
            path (str): The input path.
            nth_slash (int): The index of the slash to split at.

        Returns:
            str: The path segment after the nth slash.
        """
        # Strip leading/trailing slashes, then split. If nth_slash is 0, it takes everything after 0 splits (the whole path).
        # If path is shorter than nth_slash, split will return a list with less elements, and [-1] will still get the last one.
        result = path.strip('/').split('/', nth_slash)[-1]
        return result

    @classmethod
    def shutdown(cls):
        """
        Gracefully shuts down the thread pool executor.
        Should be called when the handler is no longer needed.
        """
        logger.info("Shutting down ReplicaModeHandler executor...")
        cls._executor.shutdown(wait=True)
        logger.info("ReplicaModeHandler executor shut down complete.")

    def _cache_replicas(self, did, fetched_file_replicas):
        """
        Persist fetched replicas and their attached DID list atomically.
        """
        if not fetched_file_replicas:
            return

        import time
        start_time = time.time()
        count = len(fetched_file_replicas)
        
        attached_dids = [AttachedFile(did=replica.did, size=replica.size) for replica in fetched_file_replicas]
        with self._write_lock:
            self.db.set_file_replicas_bulk(self.namespace, fetched_file_replicas)
            self.db.set_attached_files(self.namespace, did, attached_dids)
        
        duration = time.time() - start_time
        logger.info("Cached %d replicas for '%s' to DB in %.2fs (%.0f replicas/sec)", 
                   count, did, duration, count/duration if duration > 0 else 0)

    def _schedule_fetch_task(self, did, worker, label):
        """
        Deduplicate concurrent fetch/refresh tasks per DID.
        """
        with self._inflight_lock:
            existing_future = self._inflight_fetches.get(did)
            if existing_future and not existing_future.done():
                logger.debug("Skipping %s for '%s' because a fetch is already in progress.", label, did)
                return
            future = self._executor.submit(worker)
            self._inflight_fetches[did] = future

        def _cleanup(_):
            with self._inflight_lock:
                current = self._inflight_fetches.get(did)
                if current is future:
                    self._inflight_fetches.pop(did, None)

        future.add_done_callback(_cleanup)
