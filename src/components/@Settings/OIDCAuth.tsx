/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025
 */

import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../TextField';
import { IRucioOIDCAuth } from '../../types';
import { Spinning } from '../Spinning';
import { SelectFileButtonTrailer } from './FilePickerPopover';

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
    color: 'var(--jp-ui-font-color2)',
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

interface IOIDCAuthProps {
  params?: IRucioOIDCAuth;
  loading?: boolean;
  onAuthParamsChange: { (val: IRucioOIDCAuth): void };
}

type MyProps = IOIDCAuthProps & React.HTMLAttributes<HTMLDivElement>;

export const OIDCAuth: React.FC<MyProps> = ({
  params = { token: '' },
  loading,
  onAuthParamsChange
}) => {
  const classes = useStyles();

  const onTokenPathChange = (token_path?: string) => {
    onAuthParamsChange({ ...params, token_path: token_path ?? '' });
  };

  const loadingSpinner = (
    <div className={classes.loadingContainer}>
      <Spinning className={`${classes.loadingIcon} material-icons`}>
        hourglass_top
      </Spinning>
    </div>
  );

  return (
    <>
      <div className={classes.container}>
        <div className={classes.warning}>
          Upon authentication with the Rucio CLI, the token is usually stored in
          the path corresponding to <code>auth_token_file_path</code> {}
          <a
            style={{ color: '#3366cc' }}
            href="https://rucio.github.io/documentation/operator/configuration_parameters/#client_config"
            target="_blank"
          >
            in your Rucio configuration
          </a>
          . <br />
          If you do not know where your token is, please check with your system
          administrator.
        </div>
        <div className={classes.textFieldContainer}>
          <TextField
            placeholder="Token file path"
            // This could be a file path or the token itself,
            // but we chose not to include the raw token for security reasons
            value={params.token_path}
            onChange={e => onTokenPathChange(e.target.value)}
            disabled={loading}
            after={
              loading ? (
                loadingSpinner
              ) : (
                <SelectFileButtonTrailer
                  onFilePicked={path => onTokenPathChange(path)}
                />
              )
            }
          />
        </div>
      </div>
    </>
  );
};
