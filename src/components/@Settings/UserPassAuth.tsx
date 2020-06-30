import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../TextField';
import { RucioUserpassAuth } from '../../types';

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
  }
});

interface UserPassAuthProps {
  params?: RucioUserpassAuth;
  onChange: { (val: RucioUserpassAuth): void };
}

export const UserPassAuth: React.FC<UserPassAuthProps> = ({
  params = { username: '', password: '', account: '' },
  onChange
}) => {
  const classes = useStyles();

  const onUsernameChange = (username: string) => {
    onChange({ ...params, username });
  };

  const onPasswordChange = (password: string) => {
    onChange({ ...params, password });
  };

  const onAccountChange = (account?: string) => {
    onChange({ ...params, account });
  };

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
          />
        </div>
        <div className={classes.warning}>Your password will be stored in plain text inside your user directory.</div>
        <div className={classes.textFieldContainer}>
          <div className={classes.label}>Account (optional)</div>
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
