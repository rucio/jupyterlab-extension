import React from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { UIStore, initialState } from '../stores/UIStore';
import { Button } from '../components/Button';

const useStyles = createUseStyles({
  container: {
    padding: '16px'
  },
  label: {
    color: '#808080'
  },
  instanceName: {
    fontSize: '16pt'
  },
  buttonContainer: {
    marginTop: '16px'
  }
});

export const Info: React.FunctionComponent = () => {
  const classes = useStyles();
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const changeInstance = () => {
    UIStore.update(s => initialState);
  };

  return (
    <div className={classes.container}>
      <div className={classes.label}>Active Instance</div>
      <div className={classes.instanceName}>{activeInstance.displayName}</div>
      <div className={classes.buttonContainer}>
        <Button block onClick={() => changeInstance()}>
          Change Instance
        </Button>
      </div>
    </div>
  );
};
