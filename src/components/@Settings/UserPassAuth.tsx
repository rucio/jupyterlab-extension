import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../TextField';
import { HorizontalHeading } from '../HorizontalHeading';

const useStyles = createUseStyles({
  container: {
    padding: '8px 16px 8px 16px'
  },
  textFieldContainer: {
    margin: '8px 0 8px 0'
  },
  warning: {
    margin: '8px 8px 16px 8px',
    color: '#808080',
    fontSize: '9pt'
  }
});

export const UserPassAuth: React.FC = () => {
  const classes = useStyles();

  return (
    <>
      <HorizontalHeading title="Username &amp; Password" />
      <div className={classes.container}>
        <div className={classes.textFieldContainer}>
          <TextField placeholder="Username" outlineColor="#d5d5d5" />
        </div>
        <div className={classes.textFieldContainer}>
          <TextField placeholder="Password" outlineColor="#d5d5d5" />
        </div>
        <div className={classes.warning}>Your password will be stored in plain text inside your user directory.</div>
        <div className={classes.textFieldContainer}>
          <TextField placeholder="Account (optional)" outlineColor="#d5d5d5" />
        </div>
      </div>
    </>
  );
};
