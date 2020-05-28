import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  container: {
    padding: '8px'
  }
});

export const MyDatasets: React.FunctionComponent = () => {
  const classes = useStyles();

  return <div className={classes.container}>My Datasets</div>;
};
