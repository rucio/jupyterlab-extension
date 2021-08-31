/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021
 */

import React, { useContext } from 'react';
import { createUseStyles } from 'react-jss';
import { Spinning } from '../Spinning';
import { withRequestAPI } from '../../utils/Actions';
import { FileUploadJob, FileUploadStatus } from '../../types';
import { JupyterLabAppContext } from '../../const';
import { UploadLogViewerWidget } from '../../widgets/UploadLogViewerWidget';

const useStyles = createUseStyles({
  listItemContainer: {
    display: 'flex',
    flexDirection: 'row',
    borderBottom: '1px solid var(--jp-border-color2)',
    padding: '8px 16px 8px 16px',
    fontSize: '9pt'
  },
  listItemIconContainer: {
    paddingRight: '8px'
  },
  listItemContent: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'stretch',
    overflow: 'hidden',
    flex: 1
  },
  did: {
    textOverflow: 'ellipsis',
    overflow: 'hidden',
    whiteSpace: 'nowrap'
  },
  variableName: {
    overflowWrap: 'break-word',
    color: 'var(--jp-ui-font-color2)'
  },
  statusIcon: {
    marginTop: '2px',
    fontSize: '9pt'
  },
  availableIcon: {
    extend: 'statusIcon',
    color: 'var(--jp-success-color0)'
  },
  notAvailableIcon: {
    extend: 'statusIcon',
    color: 'var(--jp-error-color1)'
  },
  replicatingIcon: {
    extend: 'statusIcon',
    color: 'var(--jp-rucio-yellow-color)'
  },
  pendingInjectionIcon: {
    extend: 'statusIcon',
    color: 'var(--jp-success-color0)',
    opacity: 0.5
  },
  notResolvedIcon: {
    extend: 'statusIcon',
    color: 'var(--jp-ui-font-color2)'
  },
  actionContainer: {},
  clearButton: {
    alignItems: 'center',
    padding: '4px',
    lineHeight: 0,
    cursor: 'pointer'
  },
  clearIcon: {
    color: 'var(--jp-error-color1)',
    opacity: 0.5,
    fontSize: '16px',
    lineHeight: '24px',
    '&:hover': {
      opacity: 1
    }
  },
  action: {
    fontSize: '9pt',
    color: 'var(--jp-rucio-primary-blue-color)',
    cursor: 'pointer'
  }
});

export interface UploadJobListItemProps {
  job: FileUploadJob;
  onDeleteClick?: () => void;
}

const _UploadJobListItem: React.FC<UploadJobListItemProps> = ({ job, onDeleteClick }) => {
  const classes = useStyles();

  const app = useContext(JupyterLabAppContext);
  const showLog = () => {
    const widget = new UploadLogViewerWidget(job.id);
    app?.shell.add(widget, 'main');
  };

  return (
    <div className={classes.listItemContainer}>
      <div className={classes.listItemIconContainer}>
        <StatusIcon status={job.status} />
      </div>
      <div className={classes.listItemContent}>
        <div className={classes.did}>{job.did}</div>
        <div className={classes.variableName}>
          {job.path} &rarr; {job.rse}
        </div>
        {job.status === 'FAILED' && (
          <div className={classes.action} onClick={showLog}>
            Show Log
          </div>
        )}
      </div>
      <div className={classes.actionContainer}>
        {job.status !== 'UPLOADING' && !!onDeleteClick && (
          <div className={classes.clearButton} onClick={onDeleteClick}>
            <i className={`${classes.clearIcon} material-icons`}>clear</i>
          </div>
        )}
      </div>
    </div>
  );
};

const StatusIcon: React.FC<{ status?: FileUploadStatus }> = ({ status }) => {
  const classes = useStyles();

  switch (status) {
    case 'UPLOADING':
      return <Spinning className={`${classes.replicatingIcon} material-icons`}>hourglass_top</Spinning>;
    case 'OK':
      return <i className={`${classes.availableIcon} material-icons`}>check_circle</i>;
    case 'FAILED':
      return <i className={`${classes.notAvailableIcon} material-icons`}>cancel</i>;
    default:
      return <span />;
  }
};

export const UploadJobListItem = withRequestAPI(_UploadJobListItem);
