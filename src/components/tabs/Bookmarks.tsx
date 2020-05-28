import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  container: {
    padding: '16px'
  }
});

export const Bookmarks: React.FunctionComponent = () => {
  const classes = useStyles();

  return <div className={classes.container}>My Datasets</div>;
};
