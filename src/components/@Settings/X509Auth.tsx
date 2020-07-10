import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../TextField';
import { RucioX509Auth } from '../../types';
import { Spinning } from '../Spinning';

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
  },
  loadingIcon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  loadingContainer: {
    padding: '0 8px 0 8px',
    display: 'flex',
    alignItems: 'center'
  }
});

interface X509AuthProps {
  params?: RucioX509Auth;
  loading?: boolean;
  onAuthParamsChange: { (val: RucioX509Auth): void };
}

type MyProps = X509AuthProps & React.HTMLAttributes<HTMLDivElement>;

export const X509Auth: React.FC<MyProps> = ({
  params = { certificate: '', key: '', account: '' },
  loading,
  onAuthParamsChange
}) => {
  const classes = useStyles();

  const onCertPathChange = (path: string) => {
    onAuthParamsChange({ ...params, certificate: path });
  };

  const onKeyPathChange = (path: string) => {
    onAuthParamsChange({ ...params, key: path });
  };

  const onAccountChange = (account?: string) => {
    onAuthParamsChange({ ...params, account });
  };

  const loadingSpinner = (
    <div className={classes.loadingContainer}>
      <Spinning className={`${classes.loadingIcon} material-icons`}>hourglass_top</Spinning>
    </div>
  );

  return (
    <>
      <div className={classes.container}>
        <div className={classes.textFieldContainer}>
          <TextField
            placeholder="Path to certificate file"
            outlineColor="#d5d5d5"
            value={params.certificate}
            onChange={e => onCertPathChange(e.target.value)}
            disabled={loading}
            after={loading ? loadingSpinner : undefined}
          />
        </div>
        <div className={classes.textFieldContainer}>
          <TextField
            placeholder="Path to key file (optional)"
            outlineColor="#d5d5d5"
            value={params.key}
            onChange={e => onKeyPathChange(e.target.value)}
            disabled={loading}
            after={loading ? loadingSpinner : undefined}
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
            disabled={loading}
            after={loading ? loadingSpinner : undefined}
          />
        </div>
      </div>
    </>
  );
};
