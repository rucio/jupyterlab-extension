import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  container: {
    padding: '8px',
    marginTop: '8px'
  }
});

export const Header: React.FunctionComponent = () => {
  const classes = useStyles();

  return (
    <div className={classes.container}>
      <div className="jp-logo-rucio" />
    </div>
  );
};
