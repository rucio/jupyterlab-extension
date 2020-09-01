/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
 */

import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../TextField';
import { RucioX509ProxyAuth } from '../../types';
import { Spinning } from '../Spinning';
import { FilePickerPopover } from './FilePickerPopover';

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
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  iconContainer: {
    padding: '0 8px 0 0',
    display: 'flex',
    alignItems: 'center'
  },
  action: {
    cursor: 'pointer',
    color: 'var(--jp-rucio-primary-blue-color)'
  }
});

interface X509AuthProxyProps {
  params?: RucioX509ProxyAuth;
  loading?: boolean;
  onAuthParamsChange: { (val: RucioX509ProxyAuth): void };
}

type MyProps = X509AuthProxyProps & React.HTMLAttributes<HTMLDivElement>;

export const X509ProxyAuth: React.FC<MyProps> = ({ params = { proxy: '', account: '' }, loading, onAuthParamsChange }) => {
  const classes = useStyles();

  const onProxyPathChange = (path: string) => {
    onAuthParamsChange({ ...params, proxy: path });
  };

  const onAccountChange = (account?: string) => {
    onAuthParamsChange({ ...params, account });
  };

  const loadingSpinner = (
    <div className={classes.iconContainer}>
      <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
    </div>
  );

  return (
    <>
      <div className={classes.container}>
        <div className={classes.textFieldContainer}>
          <div className={classes.label}>Proxy file path</div>
          <TextField
            placeholder="Path to proxy PEM file"
            value={params.proxy}
            onChange={e => onProxyPathChange(e.target.value)}
            disabled={loading}
            after={loading ? loadingSpinner : <SelectFileButtonTrailer onFilePicked={path => onProxyPathChange(path)} />}
          />
        </div>
        <div className={classes.textFieldContainer}>
          <div className={classes.label}>Account</div>
          <TextField
            placeholder="Account"
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

const SelectFileButtonTrailer: React.FC<{ onFilePicked: { (path: string): void } }> = ({ onFilePicked }) => {
  const classes = useStyles();

  return (
    <div className={classes.iconContainer}>
      <FilePickerPopover onFilePicked={onFilePicked}>
        <span className={`${classes.icon} ${classes.action} material-icons`}>folder</span>
      </FilePickerPopover>
    </div>
  );
};
