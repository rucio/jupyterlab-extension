import React, { useEffect, useState } from 'react';
import { createUseStyles } from 'react-jss';
import CopyToClipboard from 'react-copy-to-clipboard';
import { useStoreState } from 'pullstate';
import { UIStore } from '../../stores/UIStore';
import { Spinning } from '../Spinning';
import { withRequestAPI, WithRequestAPIProps } from '../../utils/Actions';
import { AddToNotebookPopover } from './AddToNotebookPopover';
import { withPollingManager, WithPollingManagerProps, PollingRequesterRef } from '../../utils/DIDPollingManager';

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
  path: {
    fontSize: '9pt',
    padding: 0,
    margin: '8px 0 8px 0',
    overflowWrap: 'break-word',
    cursor: 'pointer',
    '&:hover': {
      color: '#2196F3'
    },
    '& .copy': {
      display: 'none',
      fontSize: '12px'
    },
    '&:hover .copy': {
      display: 'inline'
    }
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

const _FileDIDItemDetails: React.FC<DIDItem> = ({ did, ...props }) => {
  const { actions } = props as WithRequestAPIProps;
  const { didPollingManager } = props as WithPollingManagerProps;

  const classes = useStyles();
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);
  const fileDetails = useStoreState(UIStore, s => s.fileDetails[did]);

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
    actions
      .makeFileAvailable(activeInstance.name, did)
      .then(() => enablePolling())
      .catch(e => console.log(e)); // TODO handle error
  };

  return (
    <div className={classes.container}>
      {!fileDetails && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
          <span className={classes.statusText}>Loading...</span>
        </div>
      )}
      {!!fileDetails && fileDetails.status === 'OK' && <FileAvailable did={did} path={fileDetails.path} />}
      {!!fileDetails && fileDetails.status === 'NOT_AVAILABLE' && <FileNotAvailable onMakeAvailableClicked={makeAvailable} />}
      {!!fileDetails && fileDetails.status === 'REPLICATING' && <FileReplicating did={did} />}
      {!!fileDetails && fileDetails.status === 'STUCK' && <FileStuck />}
    </div>
  );
};

const FileAvailable: React.FC<{ did: string; path: string }> = ({ did, path }) => {
  const classes = useStyles();

  return (
    <>
      <div className={classes.statusContainer}>
        <div className={classes.statusAvailable}>
          <i className={`${classes.icon} material-icons`}>check_circle</i>
          <span className={classes.statusText}>Available</span>
        </div>
        <div className={classes.action}>
          <AddToNotebookPopover did={did} type="file">
            Add to Notebook
          </AddToNotebookPopover>
        </div>
      </div>
      <CopyToClipboard text={path}>
        <div className={classes.path}>
          {path} <i className="material-icons copy">file_copy</i>
        </div>
      </CopyToClipboard>
    </>
  );
};

const FileNotAvailable: React.FC<{ onMakeAvailableClicked?: { (): void } }> = ({ onMakeAvailableClicked }) => {
  const classes = useStyles();

  return (
    <div className={classes.statusContainer}>
      <div className={classes.statusNotAvailable}>
        <i className={`${classes.icon} material-icons`}>lens</i>
        <span className={classes.statusText}>Not Available</span>
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
        <span className={classes.statusText}>Replicating file...</span>
      </div>
      <div className={classes.action}>
        <AddToNotebookPopover did={did} type="file">
          Add to Notebook
        </AddToNotebookPopover>
      </div>
    </div>
  );
};

const FileStuck: React.FC = () => {
  const classes = useStyles();

  return (
    <div className={classes.statusNotAvailable}>
      <i className={`${classes.icon} material-icons`}>error</i>
      <span className={classes.statusText}>Someting went wrong</span>
    </div>
  );
};

export const FileDIDItemDetails = withPollingManager(withRequestAPI(_FileDIDItemDetails));
