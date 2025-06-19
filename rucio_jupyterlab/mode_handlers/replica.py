import os
import logging
from urllib.parse import urlparse
from rucio_jupyterlab.db import get_db
from rucio_jupyterlab.entity import AttachedFile, PfnFileReplica
import rucio_jupyterlab.utils as utils

logger = logging.getLogger(__name__)

class ReplicaModeHandler:
    """
    Handles replica-related operations, including fetching, status, and replication.
    """
    STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
    STATUS_REPLICATING = "REPLICATING"
    STATUS_OK = "OK"
    STATUS_STUCK = "STUCK"

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
        logger.info(f"ReplicaModeHandler initialized for namespace: {self.namespace}")

    def make_available(self, scope, name):
        """
        Initiates a replication rule to make a DID available.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.

        Returns:
            Any: The result from the Rucio API call.
        """
        logger.info(f"Attempting to make DID '{scope}:{name}' available.")
        dids = [{'scope': scope, 'name': name}]
        destination_rse = self.rucio.instance_config.get('destination_rse')
        lifetime_days = self.rucio.instance_config.get('replication_rule_lifetime_days')
        lifetime = (lifetime_days * 60 * 60 * 24) if lifetime_days else None

        logger.debug(f"Replication parameters: destination_rse='{destination_rse}', lifetime_days={lifetime_days} (calculated lifetime={lifetime})")

        try:
            replication_result = self.rucio.add_replication_rule(dids=dids, rse_expression=destination_rse, copies=1, lifetime=lifetime)
            logger.info(f"Successfully initiated replication rule for '{scope}:{name}'. Result: {replication_result}")
            return replication_result
        except Exception as e:
            logger.error(f"Failed to add replication rule for '{scope}:{name}'. Error: {e}", exc_info=True)
            raise # Re-raise the exception after logging

    def get_did_details(self, scope, name, force_fetch=False):
        """
        Retrieves details for a DID, including its replication status and path.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.
            force_fetch (bool): If True, forces fetching from Rucio instead of DB.

        Returns:
            list[dict]: A list of dictionaries, each containing status, DID, path, size, and PFN.
        """
        logger.info(f"Getting DID details for '{scope}:{name}', force_fetch={force_fetch}.")
        attached_file_replicas = self.get_attached_file_replicas(scope, name, force_fetch)
        complete = utils.find(lambda x: x.pfn is None, attached_file_replicas) is None
        logger.debug(f"Attached file replicas retrieved. Count: {len(attached_file_replicas)}. All PFNs present (complete): {complete}")

        status = ReplicaModeHandler.STATUS_NOT_AVAILABLE
        if not complete:
            logger.debug("PNFs are not complete, determining DID status from replication rule.")
            status = self.get_did_status(scope, name)
            logger.debug(f"Determined DID status: {status}")
        else:
            logger.debug("All PFNs are complete, assuming OK status for individual files unless otherwise specified.")

        def result_mapper(file_replica, _):
            file_did = file_replica.did
            pfn = file_replica.pfn
            path = self.translate_pfn_to_path(pfn) if pfn else None
            size = file_replica.size

            logger.debug(f"Mapping file replica: DID='{file_did}', PFN='{pfn}', Size={size}, Path='{path}'")

            if path is None:
                # This is to handle newly-attached files in which the replication rule hasn't been reevaluated by the judger daemon.
                result_status = status if status != ReplicaModeHandler.STATUS_OK else ReplicaModeHandler.STATUS_REPLICATING
                logger.debug(f"Path is None for '{file_did}'. Setting status to '{result_status}'.")
                return dict(status=result_status, did=file_did, path=None, size=size, pfn=pfn)

            logger.debug(f"Path found for '{file_did}'. Setting status to '{ReplicaModeHandler.STATUS_OK}'.")
            return dict(status=ReplicaModeHandler.STATUS_OK, did=file_did, path=path, size=size, pfn=pfn)

        results = utils.map(attached_file_replicas, result_mapper)
        logger.info(f"Finished getting DID details for '{scope}:{name}'. Returned {len(results)} results.")
        logger.debug(f"Full results: {results}")
        return results

    def get_attached_file_replicas(self, scope, name, force_fetch=False):
        """
        Gets attached file replicas, either from the database or by fetching from Rucio.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.
            force_fetch (bool): If True, forces fetching from Rucio.

        Returns:
            list[PfnFileReplica]: A list of PfnFileReplica objects.
        """
        logger.info(f"Getting attached file replicas for '{scope}:{name}', force_fetch={force_fetch}.")
        did = scope + ':' + name
        attached_files = None
        if not force_fetch:
            attached_files = self.db.get_attached_files(self.namespace, did)
            if attached_files:
                logger.debug(f"Found {len(attached_files)} attached files in DB for '{did}'.")
            else:
                logger.debug(f"No attached files found in DB for '{did}'.")

        pfn_file_replicas = None
        if attached_files:
            pfn_file_replicas = self.get_all_pfn_file_replicas_from_db(attached_files)
            if pfn_file_replicas:
                logger.debug(f"Successfully retrieved PFN file replicas from DB for '{did}'. Count: {len(pfn_file_replicas)}")
            else:
                logger.debug(f"Failed to retrieve all PFN file replicas from DB for '{did}'. Will fetch.")

        if pfn_file_replicas is None:
            logger.info(f"Fetching attached PFN file replicas from Rucio for '{did}'.")
            pfn_file_replicas = self.fetch_attached_pfn_file_replicas(scope, name)
            logger.debug(f"Fetched {len(pfn_file_replicas)} PFN file replicas from Rucio for '{did}'.")

        logger.info(f"Returning {len(pfn_file_replicas)} attached file replicas for '{did}'.")
        return pfn_file_replicas

    def get_all_pfn_file_replicas_from_db(self, attached_files):
        """
        Retrieves all PFN file replicas from the database based on a list of attached files.

        Args:
            attached_files (list[AttachedFile]): A list of AttachedFile objects.

        Returns:
            list[PfnFileReplica] or None: A list of PfnFileReplica objects if all found, else None.
        """
        logger.debug(f"Attempting to get {len(attached_files)} PFN file replicas from DB.")
        pfn_file_replicas = []
        for attached_file in attached_files:
            file_did = attached_file.did
            db_file_replica = self.db.get_file_replica(self.namespace, file_did)

            if db_file_replica is None:
                logger.warning(f"File replica for '{file_did}' not found in DB. Returning None for this batch.")
                return None

            pfn_file_replica = PfnFileReplica(did=db_file_replica.did, pfn=db_file_replica.pfn, size=db_file_replica.size)
            pfn_file_replicas.append(pfn_file_replica)
            logger.debug(f"Added DB file replica: '{file_did}' (PFN: {db_file_replica.pfn}, Size: {db_file_replica.size})")

        logger.debug(f"Successfully retrieved all {len(pfn_file_replicas)} PFN file replicas from DB.")
        return pfn_file_replicas

    def fetch_attached_pfn_file_replicas(self, scope, name):
        """
        Fetches PFN file replicas from Rucio and stores them in the database.

        Args:
            scope (str): The scope of the DID.
            name (str): The name of the DID.

        Returns:
            list[PfnFileReplica]: A list of fetched PfnFileReplica objects.
        """
        logger.info(f"Fetching and storing attached PFN file replicas for '{scope}:{name}' from Rucio.")
        pfn_file_replicas = []
        attached_dids = []
        fetched_file_replicas = self.fetch_file_replicas(scope, name)
        logger.debug(f"Rucio returned {len(fetched_file_replicas)} file replicas for '{scope}:{name}'.")

        for pfn_file_replica in fetched_file_replicas:
            self.db.set_file_replica(self.namespace, file_did=pfn_file_replica.did, pfn=pfn_file_replica.pfn, size=pfn_file_replica.size)
            pfn_file_replicas.append(pfn_file_replica)
            attached_dids.append(AttachedFile(did=pfn_file_replica.did, size=pfn_file_replica.size))
            logger.debug(f"Stored file replica for '{pfn_file_replica.did}' (PFN: {pfn_file_replica.pfn}) in DB.")

        did = scope + ':' + name
        self.db.set_attached_files(self.namespace, did, attached_dids)
        logger.info(f"Stored {len(attached_dids)} attached DIDs for '{did}' in DB.")

        logger.debug(f"Returning {len(pfn_file_replicas)} fetched PFN file replicas.")
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
        logger.info(f"Fetching file replicas from Rucio for '{scope}:{name}'.")
        destination_rse = self.rucio.instance_config.get('destination_rse')
        logger.debug(f"Target destination RSE: '{destination_rse}'.")

        replicas = []
        try:
            rucio_replicas = self.rucio.get_replicas(scope, name)
            logger.debug(f"Rucio returned {len(rucio_replicas)} raw replicas for '{scope}:{name}'.")
        except Exception as e:
            logger.error(f"Failed to fetch replicas from Rucio for '{scope}:{name}'. Error: {e}", exc_info=True)
            return [] # Return empty list on error

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
                        logger.debug(f"Found AVAILABLE PFN '{pfn}' on '{destination_rse}' for '{scope}:{name}'.")
                    else:
                        logger.warning(f"No PFNs listed for available replica on '{destination_rse}' for '{scope}:{name}'.")
                else:
                    logger.debug(f"Replica on '{destination_rse}' for '{scope}:{name}' is in state: '{states[destination_rse]}', not AVAILABLE.")
            else:
                logger.debug(f"No replica found on '{destination_rse}' or no state info for '{scope}:{name}'. Rses: {rses.keys()}, States: {states}")

            did = scope + ':' + name
            return PfnFileReplica(pfn=pfn, did=did, size=size)

        replicas = utils.map(rucio_replicas, rucio_replica_mapper)
        logger.info(f"Finished mapping {len(replicas)} Rucio replicas for '{scope}:{name}'.")
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
        logger.info(f"Getting DID status for '{scope}:{name}'.")
        status = ReplicaModeHandler.STATUS_NOT_AVAILABLE
        replication_rule = self.fetch_replication_rule_by_did(scope, name)
        if replication_rule is not None:
            _, replication_status, _ = replication_rule
            status = replication_status
            logger.debug(f"Replication rule found, status: '{status}'.")
        else:
            logger.debug(f"No replication rule found for '{scope}:{name}'. Status remains '{status}'.")

        logger.info(f"Determined DID status for '{scope}:{name}': {status}.")
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
        logger.info(f"Fetching replication rule for DID '{scope}:{name}'.")
        destination_rse = self.rucio.instance_config.get('destination_rse')
        logger.debug(f"Filtering rules for destination RSE: '{destination_rse}'.")

        try:
            rules = self.rucio.get_rules(scope, name)
            logger.debug(f"Rucio returned {len(rules)} rules for '{scope}:{name}'.")
        except Exception as e:
            logger.error(f"Failed to fetch rules from Rucio for '{scope}:{name}'. Error: {e}", exc_info=True)
            return None # Return None on error

        filtered_rules = utils.filter(rules, lambda x, _: x['rse_expression'] == destination_rse)

        if filtered_rules:
            replication_rule = filtered_rules[0]
            rule_id = replication_rule.get('id')
            parsed_status = self.parse_rule_status(replication_rule.get('state'))
            expires_at = replication_rule.get('expires_at')
            logger.info(f"Found replication rule for '{scope}:{name}': ID={rule_id}, Status='{parsed_status}', Expires='{expires_at}'.")
            return (rule_id, parsed_status, expires_at)
        else:
            logger.info(f"No replication rule found for '{scope}:{name}' matching destination RSE '{destination_rse}'.")
            return None

    def parse_rule_status(self, status):
        """
        Parses a Rucio rule status string into a standardized ReplicaModeHandler status.

        Args:
            status (str): The raw Rucio rule status.

        Returns:
            str: The parsed status.
        """
        logger.debug(f"Parsing Rucio rule status: '{status}'.")
        if status == 'OK':
            parsed_status = ReplicaModeHandler.STATUS_OK
        elif status == 'REPLICATING':
            parsed_status = ReplicaModeHandler.STATUS_REPLICATING
        else:
            parsed_status = ReplicaModeHandler.STATUS_STUCK
            logger.warning(f"Unknown Rucio rule status '{status}' parsed as '{parsed_status}'.")
        logger.debug(f"Parsed status: '{parsed_status}'.")
        return parsed_status

    def translate_pfn_to_path(self, pfn):
        """
        Translates a PFN (Physical File Name) to a local file path.

        Args:
            pfn (str): The PFN to translate.

        Returns:
            str: The translated local file path.
        """
        logger.debug(f"Translating PFN '{pfn}' to local path.")
        instance_config = self.rucio.instance_config
        prefix_path = instance_config.get('rse_mount_path')
        path_begins_at = instance_config.get('path_begins_at', 0)

        logger.debug(f"Instance config: rse_mount_path='{prefix_path}', path_begins_at={path_begins_at}.")

        path = urlparse(pfn).path
        logger.debug(f"Parsed path from PFN: '{path}'.")
        suffix_path = self.get_path_after_nth_slash(path, path_begins_at)
        logger.debug(f"Suffix path after {path_begins_at} slashes: '{suffix_path}'.")

        full_path = os.path.join(prefix_path, suffix_path)
        logger.debug(f"Combined full path: '{full_path}'.")
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
        logger.debug(f"Getting path after {nth_slash}th slash for path: '{path}'.")
        # Strip leading/trailing slashes, then split. If nth_slash is 0, it takes everything after 0 splits (the whole path).
        # If path is shorter than nth_slash, split will return a list with less elements, and [-1] will still get the last one.
        result = path.strip('/').split('/', nth_slash)[-1]
        logger.debug(f"Result: '{result}'.")
        return result

