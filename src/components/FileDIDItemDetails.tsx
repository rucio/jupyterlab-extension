import React, { useEffect } from 'react';
import { createUseStyles } from 'react-jss';
import CopyToClipboard from 'react-copy-to-clipboard';
import qs from 'querystring';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../stores/ExtensionStore';
import { FileDIDDetails } from '../types';
import { requestAPI } from '../utils/ApiRequest';
import { Spinning } from './Spinning';

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

export const FileDIDItemDetails: React.FC<DIDItem> = ({ did }) => {
  const classes = useStyles();
  const activeInstance = useStoreState(ExtensionStore, s => s.activeInstance);
  const fileDetails = useStoreState(ExtensionStore, s => s.fileDetails[did]);
  const setFileDetails = (details: FileDIDDetails) => {
    ExtensionStore.update(s => {
      s.fileDetails[did] = details;
    });
  };

  const fetchFileDetails = (poll = false) => {
    const query = {
      namespace: activeInstance.name,
      poll: poll ? 1 : undefined,
      did
    };

    requestAPI<FileDIDDetails>('file?' + qs.encode(query))
      .then(file => {
        setFileDetails(file);
        if (file.status === 'REPLICATING') {
          enablePolling();
        } else {
          disablePolling();
        }
      });
  };

  let pollInterval: number | undefined = undefined;

  const enablePolling = () => {
    if (pollInterval === undefined) {
      pollInterval = window.setInterval(() => {
        fetchFileDetails(true);
      }, 5000); // TODO change 5s?
    }
  }

  const disablePolling = () => {
    if (pollInterval !== undefined) {
      window.clearInterval(pollInterval);
      pollInterval = undefined;
    }
  }

  useEffect(() => {
    if (!fileDetails) {
      fetchFileDetails();
    } else {
      if (fileDetails.status === 'REPLICATING') {
        enablePolling();
      }
    }

    return () => {
      disablePolling();
    }
  });

  const makeAvailable = () => {
    setFileDetails({ ...fileDetails, status: 'REPLICATING' });
    setTimeout(() => {
      setFileDetails({ ...fileDetails, status: 'OK' });
    }, 3000);
  };

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
      {!!fileDetails && fileDetails.status === 'OK' && (
        <FileAvailable path={fileDetails.path} />
      )}
      {!!fileDetails && fileDetails.status === 'NOT_AVAILABLE' && (
        <FileNotAvailable onMakeAvailableClicked={makeAvailable} />
      )}
      {!!fileDetails && fileDetails.status === 'REPLICATING' && (
        <FileReplicating />
      )}
      {!!fileDetails && fileDetails.status === 'STUCK' && <FileStuck />}
    </div>
  );
};

const FileAvailable: React.FC<{ path: string }> = ({ path }) => {
  const classes = useStyles();

  return (
    <>
      <div className={classes.statusAvailable}>
        <i className={`${classes.icon} material-icons`}>check_circle</i>
        <span className={classes.statusText}>Available</span>
      </div>
      <CopyToClipboard text={path}>
        <div className={classes.path}>
          {path} <i className="material-icons copy">file_copy</i>
        </div>
      </CopyToClipboard>
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
        <span className={classes.statusText}>Not Available</span>
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
      <span className={classes.statusText}>Replicating file...</span>
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
