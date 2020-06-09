import React from 'react';
import { createUseStyles } from 'react-jss';
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

export const ContainerDIDItemDetails: React.FC<DIDItem> = ({ did }) => {
  const classes = useStyles();

  return (
    <div className={classes.container}>
      <FilePartiallyAvailable />
      {false && <FileAvailable />}
      {false && <FileNotAvailable />}
      {false && <FileReplicating />}
      {false && <FileStuck />}
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
