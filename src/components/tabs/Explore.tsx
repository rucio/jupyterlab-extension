import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  container: {
    padding: '16px'
  }
});

export const Explore: React.FunctionComponent = () => {
  const classes = useStyles();

  return <div className={classes.container}>Explore</div>;
};
