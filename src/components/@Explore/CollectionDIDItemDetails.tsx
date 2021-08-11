/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
 */

import React, { useEffect, useMemo, useState } from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { EXTENSION_ID } from '../../const';
import { UIStore } from '../../stores/UIStore';
import { Spinning } from '../Spinning';
import { withRequestAPI, WithRequestAPIProps } from '../../utils/Actions';
import { AddToNotebookPopover } from './AddToNotebookPopover';
import { computeCollectionState } from '../../utils/Helpers';
import { PollingRequesterRef, withPollingManager, WithPollingManagerProps } from '../../utils/DIDPollingManager';

const useStyles = createUseStyles({
  container: {
    padding: '4px 16px 4px 16px',
    backgroundColor: 'var(--jp-layout-color2)',
    boxSizing: 'border-box',
    height: '32px',
    alignItems: 'center'
  },
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  loading: {
    color: 'var(--jp-ui-font-color2)'
  },
  statusText: {
    fontSize: '9pt',
    verticalAlign: 'middle',
    paddingLeft: '4px',
    flex: 1,
    textOverflow: 'ellipsis',
    overflow: 'hidden',
    whiteSpace: 'nowrap'
  },
  clickableStatusText: {
    extend: 'statusText',
    '& a:hover': {
      textDecoration: 'underline',
      cursor: 'pointer'
    }
  },
  statusContainer: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1
  },
  statusAvailable: {
    extend: 'statusContainer',
    color: 'var(--jp-success-color0)'
  },
  statusPartiallyAvailable: {
    extend: 'statusContainer',
    color: 'var(--jp-rucio-yellow-color)'
  },
  statusEmpty: {
    extend: 'statusContainer',
    color: 'var(--jp-rucio-yellow-color)'
  },
  statusNotAvailable: {
    extend: 'statusContainer',
    color: 'var(--jp-error-color1)'
  },
  statusReplicating: {
    extend: 'statusContainer',
    color: 'var(--jp-rucio-yellow-color)'
  },
  action: {
    fontSize: '9pt',
    color: 'var(--jp-rucio-primary-blue-color)',
    cursor: 'pointer'
  }
});

export interface DIDItem {
  did: string;
}

const _CollectionDIDItemDetails: React.FC<DIDItem> = ({ did, ...props }) => {
  const classes = useStyles();

  const { actions } = props as WithRequestAPIProps;
  const { didPollingManager } = props as WithPollingManagerProps;

  const collectionAttachedFiles = useStoreState(UIStore, s => s.collectionDetails[did]);
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const [pollingRequesterRef] = useState(() => new PollingRequesterRef());

  const enablePolling = () => {
    didPollingManager.requestPolling(did, 'collection', pollingRequesterRef);
  };

  const disablePolling = () => {
    didPollingManager.disablePolling(did, pollingRequesterRef);
  };

  useEffect(() => {
    enablePolling();

    return () => {
      disablePolling();
    };
  }, []);

  const makeAvailable = () => {
    if (!activeInstance) {
      return;
    }

    actions
      ?.makeCollectionAvailable(activeInstance.name, did)
      .then(() => enablePolling())
      .catch(e => console.log(e)); // TODO handle error
  };

  const collectionState = useMemo(() => {
    return collectionAttachedFiles ? computeCollectionState(collectionAttachedFiles) : undefined;
  }, [collectionAttachedFiles]);

  const settings = ServerConnection.makeSettings();
  const redirectorUrl = URLExt.join(settings.baseUrl, EXTENSION_ID, 'open-replication-rule');
  const showReplicationRuleUrl =
    activeInstance?.webuiUrl && activeInstance.mode === 'replica'
      ? `${redirectorUrl}?namespace=${activeInstance?.name}&did=${did}`
      : undefined;

  return (
    <div className={classes.container}>
      {!collectionAttachedFiles && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
          <span className={classes.statusText}>Loading...</span>
        </div>
      )}
      {collectionState === 'AVAILABLE' && <FileAvailable did={did} showReplicationRuleUrl={showReplicationRuleUrl} />}
      {collectionState === 'PARTIALLY_AVAILABLE' && (
        <FilePartiallyAvailable onMakeAvailableClicked={makeAvailable} showReplicationRuleUrl={showReplicationRuleUrl} />
      )}
      {collectionState === 'NOT_AVAILABLE' && <FileNotAvailable onMakeAvailableClicked={makeAvailable} />}
      {collectionState === 'REPLICATING' && <FileReplicating did={did} showReplicationRuleUrl={showReplicationRuleUrl} />}
      {collectionState === 'STUCK' && (
        <FileStuck
          onMakeAvailableClicked={activeInstance?.mode === 'download' ? makeAvailable : undefined}
          showReplicationRuleUrl={showReplicationRuleUrl}
        />
      )}
      {collectionState === 'EMPTY' && <FileEmpty />}
    </div>
  );
};

const FileAvailable: React.FC<{ did: string; showReplicationRuleUrl?: string }> = ({ did, showReplicationRuleUrl }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusAvailable}>
      <i className={`${classes.icon} material-icons`}>check_circle</i>
      {showReplicationRuleUrl && (
        <div className={classes.clickableStatusText}>
          <a href={showReplicationRuleUrl} target="_blank" rel="noreferrer" title="Show replication rule">
            All files available
          </a>
        </div>
      )}
      {!showReplicationRuleUrl && <div className={classes.statusText}>All files available</div>}
      <div className={classes.action}>
        <AddToNotebookPopover did={did} type="collection">
          Add to Notebook
        </AddToNotebookPopover>
      </div>
    </div>
  );
};

const FileNotAvailable: React.FC<{ onMakeAvailableClicked?: () => void }> = ({ onMakeAvailableClicked }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusNotAvailable}>
      <i className={`${classes.icon} material-icons`}>lens</i>
      <div className={classes.statusText}>Not available</div>
      <div className={classes.action} onClick={onMakeAvailableClicked}>
        Make Available
      </div>
    </div>
  );
};

const FilePartiallyAvailable: React.FC<{
  onMakeAvailableClicked?: () => void;
  showReplicationRuleUrl?: string;
}> = ({ onMakeAvailableClicked, showReplicationRuleUrl }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusPartiallyAvailable}>
      <i className={`${classes.icon} material-icons`}>lens</i>
      {showReplicationRuleUrl && (
        <div className={classes.clickableStatusText}>
          <a href={showReplicationRuleUrl} target="_blank" rel="noreferrer" title="Show replication rule">
            Partially available
          </a>
        </div>
      )}
      {!showReplicationRuleUrl && <div className={classes.statusText}>Partially available</div>}
      <div className={classes.action} onClick={onMakeAvailableClicked}>
        Make Available
      </div>
    </div>
  );
};

const FileReplicating: React.FC<{ did: string; showReplicationRuleUrl?: string }> = ({ did, showReplicationRuleUrl }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusReplicating}>
      <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
      {showReplicationRuleUrl && (
        <div className={classes.clickableStatusText}>
          <a href={showReplicationRuleUrl} target="_blank" rel="noreferrer" title="Show replication rule">
            Replicating files...
          </a>
        </div>
      )}
      {!showReplicationRuleUrl && <div className={classes.statusText}>Replicating files...</div>}
      <div className={classes.action}>
        <AddToNotebookPopover did={did} type="collection">
          Add to Notebook
        </AddToNotebookPopover>
      </div>
    </div>
  );
};

const FileStuck: React.FC<{ onMakeAvailableClicked?: () => void; showReplicationRuleUrl?: string }> = ({
  onMakeAvailableClicked,
  showReplicationRuleUrl
}) => {
  const classes = useStyles();

  return (
    <div className={classes.statusNotAvailable}>
      <i className={`${classes.icon} material-icons`}>error</i>
      {showReplicationRuleUrl && (
        <div className={classes.clickableStatusText}>
          <a href={showReplicationRuleUrl} target="_blank" rel="noreferrer" title="Show replication rule">
            Something went wrong
          </a>
        </div>
      )}
      {!showReplicationRuleUrl && <div className={classes.statusText}>Something went wrong</div>}
      {onMakeAvailableClicked && (
        <div className={classes.action} onClick={onMakeAvailableClicked}>
          Make Available
        </div>
      )}
    </div>
  );
};

const FileEmpty: React.FC = () => {
  const classes = useStyles();

  return (
    <div className={classes.statusEmpty}>
      <i className={`${classes.icon} material-icons`}>warning</i>
      <div className={classes.statusText}>Collection is empty</div>
    </div>
  );
};

export const CollectionDIDItemDetails = withPollingManager(withRequestAPI(_CollectionDIDItemDetails));
