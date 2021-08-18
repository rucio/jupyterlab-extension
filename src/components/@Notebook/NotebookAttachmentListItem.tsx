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

import React, { useEffect, useMemo } from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { NotebookDIDAttachment, FileStatus, CollectionStatus, ResolveStatus } from '../../types';
import { Spinning } from '../Spinning';
import { WithRequestAPIProps, withRequestAPI } from '../../utils/Actions';
import { UIStore } from '../../stores/UIStore';
import { computeCollectionState } from '../../utils/Helpers';
import { ExtensionStore } from '../../stores/ExtensionStore';

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

export interface NotebookAttachmentListItemProps {
  attachment: NotebookDIDAttachment;
  status?: ResolveStatus;
}

const _NotebookAttachmentListItem: React.FC<NotebookAttachmentListItemProps> = ({ attachment, status, ...props }) => {
  const classes = useStyles();
  const { actions } = props as WithRequestAPIProps;
  const { did, type } = attachment;

  const fileDetails = useStoreState(UIStore, s => s.fileDetails[did]);
  const collectionDetails = useStoreState(UIStore, s => s.collectionDetails[did]);
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  useEffect(() => {
    if (!activeInstance) {
      return;
    }
    if (type === 'file') {
      actions.getFileDIDDetails(activeInstance.name, did);
    } else {
      actions.getCollectionDIDDetails(activeInstance.name, did);
    }
  }, []);

  const deleteAttachment = () => {
    ExtensionStore.update(s => {
      s.activeNotebookAttachment = s.activeNotebookAttachment?.filter(a => a.did !== did);
    });
  };

  const collectionState = useMemo(() => {
    return collectionDetails ? computeCollectionState(collectionDetails) : undefined;
  }, [collectionDetails]);

  const shouldDisplayMakeAvailableButton = (() => {
    const isExtensionInDownloadMode = activeInstance?.mode === 'download';

    if (type === 'file') {
      return fileDetails?.status === 'NOT_AVAILABLE' || (fileDetails?.status === 'STUCK' && isExtensionInDownloadMode);
    } else if (type === 'collection') {
      return (
        collectionState === 'NOT_AVAILABLE' ||
        collectionState === 'PARTIALLY_AVAILABLE' ||
        (collectionState === 'STUCK' && isExtensionInDownloadMode)
      );
    }

    return false;
  })();

  const makeAvailable = () => {
    if (!activeInstance) {
      return;
    }

    const { did, type } = attachment;
    if (type === 'file') {
      actions.makeFileAvailable(activeInstance.name, did);
    } else {
      actions.makeCollectionAvailable(activeInstance.name, did);
    }
  };

  return (
    <div className={classes.listItemContainer}>
      <div className={classes.listItemIconContainer}>
        {!fileDetails && !collectionDetails && <ResolverStatusIcon status={status} />}
        {!!fileDetails && type === 'file' && <FileStatusIcon status={fileDetails.status} resolverStatus={status} />}
        {!!collectionState && type === 'collection' && (
          <CollectionStatusIcon status={collectionState} resolverStatus={status} />
        )}
      </div>
      <div className={classes.listItemContent}>
        <div className={classes.did}>{attachment.did}</div>
        <div className={classes.variableName}>{attachment.variableName}</div>
        {shouldDisplayMakeAvailableButton && (
          <div className={classes.action} onClick={makeAvailable}>
            Make Available
          </div>
        )}
      </div>
      <div className={classes.actionContainer}>
        <div className={classes.clearButton} onClick={deleteAttachment}>
          <i className={`${classes.clearIcon} material-icons`}>clear</i>
        </div>
      </div>
    </div>
  );
};

const ResolverStatusIcon: React.FC<{ status?: ResolveStatus }> = ({ status }) => {
  const classes = useStyles();

  switch (status) {
    case 'RESOLVING':
      return <Spinning className={`${classes.statusIcon} material-icons`}>hourglass_top</Spinning>;
    case 'PENDING_INJECTION':
      return <i className={`${classes.pendingInjectionIcon} material-icons`}>lens</i>;
    case 'READY':
      return <i className={`${classes.availableIcon} material-icons`}>check_circle</i>;
    case 'FAILED':
      return <i className={`${classes.notAvailableIcon} material-icons`}>cancel</i>;
    default:
      return <i className={`${classes.notResolvedIcon} material-icons`}>lens</i>;
  }
};

const FileStatusIcon: React.FC<{ status?: FileStatus; resolverStatus?: ResolveStatus }> = ({ status, resolverStatus }) => {
  const classes = useStyles();

  switch (status) {
    case 'REPLICATING':
      return <Spinning className={`${classes.replicatingIcon} material-icons`}>hourglass_top</Spinning>;
    case 'NOT_AVAILABLE':
    case 'STUCK':
      return <i className={`${classes.notAvailableIcon} material-icons`}>lens</i>;
    default:
      return <ResolverStatusIcon status={resolverStatus} />;
  }
};

const CollectionStatusIcon: React.FC<{ status?: CollectionStatus; resolverStatus?: ResolveStatus }> = ({
  status,
  resolverStatus
}) => {
  const classes = useStyles();

  switch (status) {
    case 'REPLICATING':
      return <Spinning className={`${classes.replicatingIcon} material-icons`}>hourglass_top</Spinning>;
    case 'NOT_AVAILABLE':
    case 'STUCK':
    case 'PARTIALLY_AVAILABLE':
      return <i className={`${classes.notAvailableIcon} material-icons`}>lens</i>;
    default:
      return <ResolverStatusIcon status={resolverStatus} />;
  }
};

export const NotebookAttachmentListItem = withRequestAPI(_NotebookAttachmentListItem);
