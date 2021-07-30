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

import React, { useState, useEffect, useCallback } from 'react';
import Popover from 'react-popover';
import CopyToClipboard from 'react-copy-to-clipboard';
import { createUseStyles } from 'react-jss';
import { FixedSizeList } from 'react-window';
import { useStoreState } from 'pullstate';
import { UIStore } from '../../stores/UIStore';
import { AttachedFile } from '../../types';
import { actions } from '../../utils/Actions';
import { Spinning } from '../Spinning';
import { toHumanReadableSize } from '../../utils/Helpers';

const useStyles = createUseStyles({
  main: {
    width: '300px',
    background: 'var(--jp-layout-color1)',
    color: 'var(--jp-ui-font-color1)'
  },
  heading: {
    background: 'var(--jp-layout-color2)',
    color: 'var(--jp-ui-font-color2)',
    padding: '8px',
    borderBottom: '1px solid var(--jp-border-color2)',
    fontSize: '9pt',
    display: 'flex',
    flexDirection: 'row'
  },
  headingText: {
    textOverflow: 'ellipsis',
    overflow: 'hidden',
    whiteSpace: 'nowrap',
    flex: 1
  },
  content: {
    fontSize: '10pt',
    overflow: 'auto',
    maxHeight: '250px',
    '&.loading': {
      opacity: 0.4,
      pointerEvents: 'none'
    }
  },
  loading: {
    padding: '8px',
    boxSizing: 'border-box'
  },
  icon: {
    fontSize: '16px',
    verticalAlign: 'middle'
  },
  iconText: {
    fontSize: '9pt',
    verticalAlign: 'middle',
    paddingLeft: '4px'
  },
  headingCloseButton: {
    extend: 'icon',
    cursor: 'pointer'
  },
  listItem: {
    display: 'flex',
    padding: '8px',
    borderBottom: '1px solid var(--jp-border-color2)',
    flexDirection: 'row',
    fontSize: '9pt',
    alignItems: 'center',
    boxSizing: 'border-box',
    overflow: 'hidden'
  },
  textContainer: {
    flex: 1,
    textOverflow: 'ellipsis',
    overflow: 'hidden',
    whiteSpace: 'nowrap',
    cursor: 'pointer',
    '&:hover': {
      color: 'var(--jp-rucio-primary-blue-color)'
    },
    '& .copy': {
      display: 'none',
      fontSize: '12px'
    },
    '&:hover .copy': {
      display: 'inline'
    }
  },
  iconContainer: {
    lineHeight: 0,
    marginRight: '8px'
  },
  sizeContainer: {
    color: 'var(--jp-ui-font-color2)'
  },
  fileIcon: {
    extend: 'icon',
    color: '#66B100'
  },
  loadingIcon: {
    fontSize: '9pt',
    verticalAlign: 'middle'
  }
});

interface ListAttachedFilesPopoverProps {
  did: string;
}

type MyProps = React.HTMLAttributes<HTMLDivElement> & ListAttachedFilesPopoverProps;

export const ListAttachedFilesPopover: React.FC<MyProps> = ({ children, did }) => {
  const classes = useStyles();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<AttachedFile[]>([]);
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const escFunction = useCallback(event => {
    if (event.keyCode === 27) {
      setOpen(false);
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', escFunction, false);

    return () => {
      document.removeEventListener('keydown', escFunction, false);
    };
  }, []);

  const Row = ({ index, style }: any) => {
    const file = files[index];
    return <ListItem style={style} did={file.did} size={file.size} />;
  };

  const popoverBody = (
    <div className={classes.main}>
      <div className={classes.heading}>
        <div className={classes.headingText}>
          Files of <b>{did}</b>
        </div>
        <i className={`${classes.headingCloseButton} material-icons`} onClick={() => setOpen(false)}>
          close
        </i>
      </div>
      <div className={classes.content}>
        {loading && (
          <div className={classes.loading}>
            <Spinning className={`${classes.loadingIcon} material-icons`}>hourglass_top</Spinning>
            <span className={classes.iconText}>Loading...</span>
          </div>
        )}
        <FixedSizeList height={Math.min(250, 32 * files.length)} itemCount={files.length} itemSize={32} width="100%">
          {Row}
        </FixedSizeList>
      </div>
    </div>
  );

  const loadAttachedFiles = () => {
    if (!activeInstance) {
      return;
    }
    setLoading(true);
    setFiles([]);
    actions
      .fetchAttachedFileDIDs(activeInstance.name, did)
      .then(result => setFiles(result))
      .catch(e => console.log(e)) // TODO handle error
      .finally(() => setLoading(false));
  };

  const openPopover = () => {
    setOpen(true);
    loadAttachedFiles();
  };

  return (
    <Popover
      enterExitTransitionDurationMs={0}
      isOpen={open}
      preferPlace="below"
      body={popoverBody}
      onOuterAction={() => setOpen(false)}
    >
      <div onClick={openPopover}>{children}</div>
    </Popover>
  );
};

const ListItem: React.FC<{ did: string; size: number; style: any }> = ({ did, size, style }) => {
  const classes = useStyles();

  return (
    <div className={classes.listItem} style={style}>
      <div className={classes.iconContainer}>
        <i className={`${classes.fileIcon} material-icons`}>attachment</i>
      </div>
      <CopyToClipboard text={did}>
        <div className={classes.textContainer}>
          {did} <i className="material-icons copy">file_copy</i>
        </div>
      </CopyToClipboard>
      {!!size && <div className={classes.sizeContainer}>{toHumanReadableSize(size)}</div>}
    </div>
  );
};
