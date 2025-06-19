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

import React, { useEffect, useState } from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { EXTENSION_ID } from '../../const';
import { UIStore } from '../../stores/UIStore';
import { Spinning } from '../Spinning';
import { withRequestAPI, IWithRequestAPIProps } from '../../utils/Actions';
import { AddToNotebookPopover } from './AddToNotebookPopover';
import {
  withPollingManager,
  IWithPollingManagerProps,
  PollingRequesterRef
} from '../../utils/DIDPollingManager';

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

export interface IDIDItem {
  did: string;
}

const _FileDIDItemDetails: React.FC<IDIDItem> = ({ did, ...props }) => {
  const classes = useStyles();

  const [error, setError] = useState<string>();

  const { actions } = props as IWithRequestAPIProps;
  const { didPollingManager } = props as IWithPollingManagerProps;

  const fileDetails = useStoreState(UIStore, s => s.fileDetails[did]);
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const [pollingRequesterRef] = useState(() => new PollingRequesterRef());

  const enablePolling = () => {
    didPollingManager.requestPolling(did, 'file', pollingRequesterRef);
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
      ?.makeFileAvailable(activeInstance.name, did)
      .then(() => enablePolling())
      .catch(e => {
        console.error('Error making file available:', e);
        // The error 'e' is the rich ResponseError object from requestAPI
        if (e.response && e.response.status === 401) {
          setError(
            'Authentication error. Perhaps you set an invalid credential?'
          );
          return;
        }

        // The backend error message is directly available on e.error
        if (e.error) {
          setError(e.error);
        } else {
          // Fallback to the general error message if e.error is not present
          setError(e.message || 'An unknown error occurred.');
        }
      });
  };

  const settings = ServerConnection.makeSettings();
  const redirectorUrl = URLExt.join(
    settings.baseUrl,
    EXTENSION_ID,
    'open-replication-rule'
  );
  const showReplicationRuleUrl =
    activeInstance?.webuiUrl && activeInstance.mode === 'replica'
      ? `${redirectorUrl}?namespace=${activeInstance?.name}&did=${did}`
      : undefined;

  return (
    <div className={classes.container}>
      {!fileDetails && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>
            hourglass_top
          </Spinning>
          <span className={classes.statusText}>Loading...</span>
        </div>
      )}
      {!!fileDetails && fileDetails.status === 'OK' && fileDetails.path && (
        <FileAvailable
          did={did}
          path={fileDetails.path}
          showReplicationRuleUrl={showReplicationRuleUrl}
        />
      )}
      {!!fileDetails && fileDetails.status === 'NOT_AVAILABLE' && (
        <FileNotAvailable
          onMakeAvailableClicked={makeAvailable}
          error={error}
        />
      )}
      {!!fileDetails && fileDetails.status === 'REPLICATING' && (
        <FileReplicating
          did={did}
          showReplicationRuleUrl={showReplicationRuleUrl}
        />
      )}
      {!!fileDetails && fileDetails.status === 'STUCK' && (
        <FileStuck
          onMakeAvailableClicked={
            activeInstance?.mode === 'download' ? makeAvailable : undefined
          }
          error={error}
          showReplicationRuleUrl={showReplicationRuleUrl}
        />
      )}
      {!!fileDetails &&
        fileDetails.status === 'FAILED' &&
        (console.error('File details retrieval failed:', fileDetails),
        (
          <FileNotAvailable
            onMakeAvailableClicked={makeAvailable}
            error={fileDetails.error || 'Failed to retrieve file details.'}
          />
        ))}
    </div>
  );
};

const FileAvailable: React.FC<{
  did: string;
  path: string;
  showReplicationRuleUrl?: string;
}> = ({ did, path, showReplicationRuleUrl }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusAvailable}>
      <i className={`${classes.icon} material-icons`}>check_circle</i>
      {showReplicationRuleUrl && (
        <div className={classes.clickableStatusText}>
          <a
            href={showReplicationRuleUrl}
            target="_blank"
            rel="noreferrer"
            title="Show replication rule"
          >
            Available
          </a>
        </div>
      )}
      {!showReplicationRuleUrl && (
        <div className={classes.statusText}>Available</div>
      )}
      <div className={classes.action}>
        <AddToNotebookPopover did={did} type="file">
          Add to Notebook
        </AddToNotebookPopover>
      </div>
    </div>
  );
};

const FileNotAvailable: React.FC<{
  onMakeAvailableClicked?: () => void;
  error?: string; // Optional error prop to handle error messages
}> = ({ onMakeAvailableClicked, error }) => {
  // Destructure error from props
  const classes = useStyles();

  return (
    <div className={classes.statusNotAvailable}>
      {/* Conditionally render the icon and message based on the error state */}
      {error ? (
        <i className={`${classes.icon} material-icons`}>error</i>
      ) : (
        <i className={`${classes.icon} material-icons`}>lens</i>
      )}

      {/* Display the error message if it exists */}
      {error && (
        <div
          className={classes.statusText}
          style={{ color: 'var(--jp-error-color1)' }}
        >
          {error}
        </div>
      )}

      {/* Show the default text only when there is no error */}
      {!error && <div className={classes.statusText}>Not Available</div>}

      <div className={classes.action} onClick={onMakeAvailableClicked}>
        {/* Change button text based on context */}
        {error ? 'Retry' : 'Make Available'}
      </div>
    </div>
  );
};

const FileReplicating: React.FC<{
  did: string;
  showReplicationRuleUrl?: string;
}> = ({ did, showReplicationRuleUrl }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusReplicating}>
      <Spinning className={`${classes.icon} material-icons`}>
        hourglass_top
      </Spinning>
      {showReplicationRuleUrl && (
        <div className={classes.clickableStatusText}>
          <a
            href={showReplicationRuleUrl}
            target="_blank"
            rel="noreferrer"
            title="Show replication rule"
          >
            Replicating files...
          </a>
        </div>
      )}
      {!showReplicationRuleUrl && (
        <div className={classes.statusText}>Replicating files...</div>
      )}
      <div className={classes.action}>
        <AddToNotebookPopover did={did} type="collection">
          Add to Notebook
        </AddToNotebookPopover>
      </div>
    </div>
  );
};

const FileStuck: React.FC<{
  error?: string;
  onMakeAvailableClicked?: () => void;
  showReplicationRuleUrl?: string;
}> = ({ onMakeAvailableClicked, showReplicationRuleUrl, error }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusNotAvailable}>
      <i className={`${classes.icon} material-icons`}>error</i>
      {error && (
        <div
          className={classes.statusText}
          style={{ color: 'var(--jp-error-color1)' }}
        >
          {error}
        </div>
      )}
      {!error && showReplicationRuleUrl && (
        <div className={classes.clickableStatusText}>
          <a
            href={showReplicationRuleUrl}
            target="_blank"
            rel="noreferrer"
            title="Show replication rule"
          >
            Something went wrong
          </a>
        </div>
      )}
      {!error && !showReplicationRuleUrl && (
        <div className={classes.statusText}>Something went wrong</div>
      )}
      {onMakeAvailableClicked && (
        <div className={classes.action} onClick={onMakeAvailableClicked}>
          Make Available
        </div>
      )}
    </div>
  );
};

export const FileDIDItemDetails = withPollingManager(
  withRequestAPI(_FileDIDItemDetails)
);
