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

export const X509Auth: React.FC = () => {
  const classes = useStyles();

  return (
    <>
      <HorizontalHeading title="X.509 User Certificate" />
      <div className={classes.container}>
        <div className={classes.textFieldContainer}>
          <TextField placeholder="Path to certificate file" outlineColor="#d5d5d5" />
        </div>
        <div className={classes.textFieldContainer}>
          <TextField placeholder="Path to key file (optional)" outlineColor="#d5d5d5" />
        </div>
        <div className={classes.warning}>
          Enter the private key path if the certificate file does not include it. Passphrase-protected certificate is not
          supported.
        </div>
        <div className={classes.textFieldContainer}>
          <TextField placeholder="Account (optional)" outlineColor="#d5d5d5" />
        </div>
      </div>
    </>
  );
};
