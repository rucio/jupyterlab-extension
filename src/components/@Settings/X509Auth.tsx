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
import { RucioX509Auth } from '../../types';
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
    <div className={classes.iconContainer}>
      <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
    </div>
  );

  return (
    <>
      <div className={classes.container}>
        <div className={classes.textFieldContainer}>
          <div className={classes.label}>Certificate file path</div>
          <TextField
            placeholder="Path to certificate file"
            value={params.certificate}
            onChange={e => onCertPathChange(e.target.value)}
            disabled={loading}
            after={loading ? loadingSpinner : <SelectFileButtonTrailer onFilePicked={path => onCertPathChange(path)} />}
          />
        </div>
        <div className={classes.textFieldContainer}>
          <div className={classes.label}>Key file path</div>
          <TextField
            placeholder="Path to key file"
            value={params.key}
            onChange={e => onKeyPathChange(e.target.value)}
            disabled={loading}
            after={loading ? loadingSpinner : <SelectFileButtonTrailer onFilePicked={path => onKeyPathChange(path)} />}
          />
        </div>
        <div className={classes.warning}>
          Enter the private key path if the certificate file does not include it. Passphrase-protected certificate is not
          supported.
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
