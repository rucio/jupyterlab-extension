import React, { useEffect, useMemo, useState } from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { UIStore } from '../../stores/UIStore';
import { Spinning } from '../Spinning';
import { withRequestAPI, WithRequestAPIProps } from '../../utils/Actions';
import { AddToNotebookPopover } from './AddToNotebookPopover';
import { computeContainerState } from '../../utils/Helpers';
import { PollingRequesterRef, withPollingManager, WithPollingManagerProps } from '../../utils/DIDPollingManager';

const useStyles = createUseStyles({
  container: {
    padding: '0 16px 8px 16px',
    backgroundColor: '#F8F8F8'
  },
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  loading: {
    color: '#808080',
    alignItems: 'center'
  },
  statusText: {
    fontSize: '9pt',
    verticalAlign: 'middle',
    paddingLeft: '4px'
  },
  statusAvailable: {
    color: '#5a9216',
    flex: 1
  },
  statusPartiallyAvailable: {
    color: '#ffa000',
    flex: 1
  },
  statusNotAvailable: {
    color: '#dd2c00',
    flex: 1
  },
  statusReplicating: {
    color: '#ffa000',
    flex: 1
  },
  statusContainer: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center'
  },
  action: {
    fontSize: '9pt',
    color: '#2196F3',
    cursor: 'pointer'
  }
});

export interface DIDItem {
  did: string;
}

const _ContainerDIDItemDetails: React.FC<DIDItem> = ({ did, ...props }) => {
  const classes = useStyles();

  const { actions } = props as WithRequestAPIProps;
  const { didPollingManager } = props as WithPollingManagerProps;

  const activeInstance = useStoreState(UIStore, s => s.activeInstance);
  const containerAttachedFiles = useStoreState(UIStore, s => s.containerDetails[did]);

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
    actions
      .makeContainerAvailable(activeInstance.name, did)
      .then(() => enablePolling())
      .catch(e => console.log(e)); // TODO handle error
  };

  const containerState = useMemo(() => {
    return containerAttachedFiles ? computeContainerState(containerAttachedFiles) : undefined;
  }, [containerAttachedFiles]);

  return (
    <div className={classes.container}>
      {!containerAttachedFiles && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
          <span className={classes.statusText}>Loading...</span>
        </div>
      )}
      {containerState === 'AVAILABLE' && <FileAvailable did={did} />}
      {containerState === 'PARTIALLY_AVAILABLE' && <FilePartiallyAvailable onMakeAvailableClicked={makeAvailable} />}
      {containerState === 'NOT_AVAILABLE' && <FileNotAvailable onMakeAvailableClicked={makeAvailable} />}
      {containerState === 'REPLICATING' && <FileReplicating did={did} />}
      {containerState === 'STUCK' && <FileStuck onMakeAvailableClicked={makeAvailable} />}
    </div>
  );
};

const FileAvailable: React.FC<{ did: string }> = ({ did }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusContainer}>
      <div className={classes.statusAvailable}>
        <i className={`${classes.icon} material-icons`}>check_circle</i>
        <span className={classes.statusText}>All files available</span>
      </div>
      <div className={classes.action}>
        <AddToNotebookPopover did={did} type="collection">
          Add to Notebook
        </AddToNotebookPopover>
      </div>
    </div>
  );
};

const FileNotAvailable: React.FC<{ onMakeAvailableClicked?: { (): void } }> = ({ onMakeAvailableClicked }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusContainer}>
      <div className={classes.statusNotAvailable}>
        <i className={`${classes.icon} material-icons`}>lens</i>
        <span className={classes.statusText}>Not available</span>
      </div>
      <div className={classes.action} onClick={onMakeAvailableClicked}>
        Make Available
      </div>
    </div>
  );
};

const FilePartiallyAvailable: React.FC<{
  onMakeAvailableClicked?: { (): void };
}> = ({ onMakeAvailableClicked }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusContainer}>
      <div className={classes.statusPartiallyAvailable}>
        <i className={`${classes.icon} material-icons`}>lens</i>
        <span className={classes.statusText}>Partially available</span>
      </div>
      <div className={classes.action} onClick={onMakeAvailableClicked}>
        Make Available
      </div>
    </div>
  );
};

const FileReplicating: React.FC<{ did: string }> = ({ did }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusContainer}>
      <div className={classes.statusReplicating}>
        <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
        <span className={classes.statusText}>Replicating files...</span>
      </div>
      <div className={classes.action}>
        <AddToNotebookPopover did={did} type="collection">
          Add to Notebook
        </AddToNotebookPopover>
      </div>
    </div>
  );
};

const FileStuck: React.FC<{ onMakeAvailableClicked?: { (): void } }> = ({ onMakeAvailableClicked }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusContainer}>
      <div className={classes.statusNotAvailable}>
        <i className={`${classes.icon} material-icons`}>error</i>
        <span className={classes.statusText}>Something went wrong</span>
      </div>
      <div className={classes.action} onClick={onMakeAvailableClicked}>
        Make Available
      </div>
    </div>
  );
};

export const ContainerDIDItemDetails = withPollingManager(withRequestAPI(_ContainerDIDItemDetails));
