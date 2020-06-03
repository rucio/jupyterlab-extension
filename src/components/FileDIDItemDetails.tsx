import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';
import CopyToClipboard from 'react-copy-to-clipboard';

import { FileDIDDetails } from '../types';
import { Spinning } from './Spinning';

const useStyles = createUseStyles({
  container: {
    padding: '8px 16px 8px 16px',
    backgroundColor: '#F8F8F8'
  },
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
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
  const [fileDetails, setFileDetails] = useState<FileDIDDetails>({
    status: 'unavailable',
    path: '/eos/rucio/atlas/49/ad/4cd1-3287.csv'
  });

  const makeAvailable = () => {
    setFileDetails({ ...fileDetails, status: 'replicating' });
    setTimeout(() => {
      setFileDetails({ ...fileDetails, status: 'available' });
    }, 3000);
  };

  return (
    <div className={classes.container}>
      {!fileDetails && <div>Loading...</div>}
      {!!fileDetails && fileDetails.status === 'available' && (
        <FileAvailable path={fileDetails.path} />
      )}
      {!!fileDetails && fileDetails.status === 'unavailable' && (
        <FileNotAvailable onMakeAvailableClicked={makeAvailable} />
      )}
      {!!fileDetails && fileDetails.status === 'replicating' && (
        <FileReplicating />
      )}
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
