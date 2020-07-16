import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../TextField';
import { RucioUserpassAuth } from '../../types';
import { Spinning } from '../Spinning';

const useStyles = createUseStyles({
  container: {
    padding: '8px 16px 8px 16px'
  },
  label: {
    margin: '4px 0 4px 0'
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

interface UserPassAuthProps {
  params?: RucioUserpassAuth;
  loading?: boolean;
  onAuthParamsChange: { (val: RucioUserpassAuth): void };
}

type MyProps = UserPassAuthProps & React.HTMLAttributes<HTMLDivElement>;

export const UserPassAuth: React.FC<MyProps> = ({
  params = { username: '', password: '', account: '' },
  loading,
  onAuthParamsChange
}) => {
  const classes = useStyles();

  const onUsernameChange = (username: string) => {
    onAuthParamsChange({ ...params, username });
  };

  const onPasswordChange = (password: string) => {
    onAuthParamsChange({ ...params, password });
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
          <div className={classes.label}>Username</div>
          <TextField
            placeholder="Username"
            outlineColor="#d5d5d5"
            value={params.username}
            onChange={e => onUsernameChange(e.target.value)}
            disabled={loading}
            after={loading ? loadingSpinner : undefined}
          />
        </div>
        <div className={classes.textFieldContainer}>
          <div className={classes.label}>Password</div>
          <TextField
            placeholder="Password"
            type="password"
            outlineColor="#d5d5d5"
            value={params.password}
            onChange={e => onPasswordChange(e.target.value)}
            disabled={loading}
            after={loading ? loadingSpinner : undefined}
          />
        </div>
        <div className={classes.warning}>Your password will be stored in plain text inside your user directory.</div>
        <div className={classes.textFieldContainer}>
          <div className={classes.label}>Account</div>
          <TextField
            placeholder="Account"
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
