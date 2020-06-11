import React, { useEffect } from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { UIStore } from '../stores/UIStore';
import { Spinning } from './Spinning';
import { FileDIDDetails, ContainerStatus } from '../types';
import { withRequestAPI, WithRequestAPIProps } from '../utils/Actions';

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
    color: '#5a9216'
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
    color: '#ffa000'
  },
  statusNotAvailableContainer: {
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

  const activeInstance = useStoreState(UIStore, s => s.activeInstance);
  const containerAttachedFiles = useStoreState(
    UIStore,
    s => s.containerDetails[did]
  );

  const computeContainerState = (
    files: FileDIDDetails[]
  ): ContainerStatus | false => {
    if (!files) {
      return false;
    }

    if (files.length === 0) {
      return 'AVAILABLE';
    }

    const available = files.find(file => file.status === 'OK');
    const notAvailable = files.find(file => file.status === 'NOT_AVAILABLE');
    const replicating = files.find(file => file.status === 'REPLICATING');
    const stuck = files.find(file => file.status === 'STUCK');

    if (replicating) {
      return 'REPLICATING';
    }

    if (stuck) {
      return 'STUCK';
    }

    if (!available) {
      return 'NOT_AVAILABLE';
    }

    if (notAvailable) {
      return 'PARTIALLY_AVAILABLE';
    }

    return 'AVAILABLE';
  };

  const fetchDIDDetails = (poll = false) => {
    return actions.getContainerDIDDetails(activeInstance.name, did)
      .then(files => {
        const containerState = computeContainerState(files);
        if (containerState !== 'REPLICATING') {
          disablePolling();
        }
        return files;
      });
  };

  let pollInterval: number | undefined = undefined;

  const poll = () => {
    fetchDIDDetails(true);
  };

  const enablePolling = () => {
    if (pollInterval === undefined) {
      poll();
      pollInterval = window.setInterval(() => {
        poll();
      }, 10000); // TODO change 10s?
    }
  };

  const disablePolling = () => {
    if (pollInterval !== undefined) {
      window.clearInterval(pollInterval);
      pollInterval = undefined;
    }
  };

  useEffect(() => {
    if (!containerAttachedFiles) {
      fetchDIDDetails();
    } else {
      const containerState = computeContainerState(containerAttachedFiles);
      if (containerState === 'REPLICATING') {
        enablePolling();
      }
    }

    return () => {
      disablePolling();
    };
  }, []);

  const makeAvailable = () => {
    actions.makeContainerAvailable(activeInstance.name, did)
      .then(() => enablePolling())
      .catch(e => console.log(e)); // TODO handle error
  };

  const containerState = !!containerAttachedFiles ? computeContainerState(containerAttachedFiles) : undefined;

  return (
    <div className={classes.container}>
      {!containerAttachedFiles && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>
            hourglass_top
          </Spinning>
          <span className={classes.statusText}>Loading...</span>
        </div>
      )}
      {containerState === 'AVAILABLE' && <FileAvailable />}
      {containerState === 'PARTIALLY_AVAILABLE' && (
        <FilePartiallyAvailable onMakeAvailableClicked={makeAvailable} />
      )}
      {containerState === 'NOT_AVAILABLE' && (
        <FileNotAvailable onMakeAvailableClicked={makeAvailable} />
      )}
      {containerState === 'REPLICATING' && <FileReplicating />}
      {containerState === 'STUCK' && <FileStuck />}
    </div>
  );
};

const FileAvailable: React.FC = () => {
  const classes = useStyles();

  return (
    <>
      <div className={classes.statusAvailable}>
        <i className={`${classes.icon} material-icons`}>check_circle</i>
        <span className={classes.statusText}>All files available</span>
      </div>
    </>
  );
};

const FileNotAvailable: React.FC<{ onMakeAvailableClicked?: { (): void } }> = ({
  onMakeAvailableClicked
}) => {
  const classes = useStyles();

  return (
    <div className={classes.statusNotAvailableContainer}>
      <div className={classes.statusNotAvailable}>
        <i className={`${classes.icon} material-icons`}>cancel</i>
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
    <div className={classes.statusNotAvailableContainer}>
      <div className={classes.statusPartiallyAvailable}>
        <i className={`${classes.icon} material-icons`}>cancel</i>
        <span className={classes.statusText}>Partially available</span>
      </div>
      <div className={classes.action} onClick={onMakeAvailableClicked}>
        Make Available
      </div>
    </div>
  );
};

const FileReplicating: React.FC = () => {
  const classes = useStyles();

  return (
    <div className={classes.statusReplicating}>
      <Spinning className={`${classes.icon} material-icons`}>
        hourglass_top
      </Spinning>
      <span className={classes.statusText}>Replicating files...</span>
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

export const ContainerDIDItemDetails = withRequestAPI(_ContainerDIDItemDetails);