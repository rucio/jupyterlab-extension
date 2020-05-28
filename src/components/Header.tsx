import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  container: {
    padding: '16px 8px 8px 8px'
  }
});

export const Header: React.FunctionComponent<
  React.HTMLAttributes<HTMLElement>
> = props => {
  const classes = useStyles();

  return (
    <div className={classes.container} {...props}>
      <div className="jp-logo-rucio" />
    </div>
  );
};
