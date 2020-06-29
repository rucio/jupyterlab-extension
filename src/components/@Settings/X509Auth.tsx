import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../TextField';
import { RucioX509Auth } from '../../types';

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

interface X509AuthProps {
  params: RucioX509Auth;
  onChange: { (val: RucioX509Auth): void };
}

export const X509Auth: React.FC<X509AuthProps> = ({ params, onChange }) => {
  const classes = useStyles();

  const onCertPathChange = (path: string) => {
    onChange({ ...params, certificateFilePath: path });
  };

  const onKeyPathChange = (path: string) => {
    onChange({ ...params, privateKeyFilePath: path });
  };

  const onAccountChange = (account?: string) => {
    onChange({ ...params, account });
  };

  return (
    <>
      <div className={classes.container}>
        <div className={classes.textFieldContainer}>
          <TextField
            placeholder="Path to certificate file"
            outlineColor="#d5d5d5"
            value={params.certificateFilePath}
            onChange={e => onCertPathChange(e.target.value)}
          />
        </div>
        <div className={classes.textFieldContainer}>
          <TextField
            placeholder="Path to key file (optional)"
            outlineColor="#d5d5d5"
            value={params.privateKeyFilePath}
            onChange={e => onKeyPathChange(e.target.value)}
          />
        </div>
        <div className={classes.warning}>
          Enter the private key path if the certificate file does not include it. Passphrase-protected certificate is not
          supported.
        </div>
        <div className={classes.textFieldContainer}>
          <TextField
            placeholder="Account (optional)"
            outlineColor="#d5d5d5"
            value={params.account}
            onChange={e => onAccountChange(e.target.value)}
          />
        </div>
      </div>
    </>
  );
};
