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

import React, { useLayoutEffect, useRef } from 'react';
import { createUseStyles } from 'react-jss';
import { FileDIDItemDetails } from './FileDIDItemDetails';
import { CollectionDIDItemDetails } from './CollectionDIDItemDetails';
import { toHumanReadableSize } from '../../utils/Helpers';
import { ListAttachedFilesPopover } from './ListAttachedFilesPopover';

const useStyles = createUseStyles({
  listItemContainer: {
    borderBottom: '1px solid var(--jp-border-color2)',
    overflow: 'hidden',
    boxSizing: 'border-box'
  },
  listItem: {
    display: 'flex',
    flexDirection: 'row',
    fontSize: '9pt',
    alignItems: 'center',
    padding: '8px 16px 8px 16px',
    cursor: 'pointer'
  },
  listItemCollapsed: {
    extend: 'listItem',
    '&:hover': {
      backgroundColor: 'var(--jp-layout-color2)'
    }
  },
  listItemExpanded: {
    extend: 'listItem',
    backgroundColor: 'var(--jp-layout-color2)'
  },
  textContainer: {
    flex: 1,
    textOverflow: 'ellipsis',
    overflow: 'hidden',
    whiteSpace: 'nowrap'
  },
  iconContainer: {
    lineHeight: 0,
    marginRight: '8px'
  },
  icon: {
    fontSize: '16px',
    verticalAlign: 'middle'
  },
  fileIcon: {
    extend: 'icon',
    color: '#66B100'
  },
  containerIcon: {
    extend: 'icon',
    color: '#5DC0FD'
  },
  datasetIcon: {
    extend: 'icon',
    color: '#FFB100'
  },
  sizeContainer: {
    color: 'var(--jp-ui-font-color2)'
  },
  listFilesIcon: {
    extend: 'icon',
    color: '#2196F3',
    cursor: 'pointer'
  }
});

export interface IDIDItem {
  did: string;
  size?: number;
  type: 'dataset' | 'container' | 'file';
  onClick?: { (): any };
  expand?: boolean;
  style?: any;
  onHeightChange?: (height: number) => void;
}

export const DIDListItem: React.FC<IDIDItem> = ({
  did,
  size,
  type,
  onClick,
  expand,
  style,
  onHeightChange
}) => {
  const classes = useStyles();
  const contentRef = useRef<HTMLDivElement>(null);

  // The outer listItemContainer gets a fixed height from react-window (via `style`) and
  // clips to it, so expanded content that needs more room than the parent list guessed
  // (e.g. a wrapped multi-line diagnostic message) gets silently cut off instead of
  // growing the row. Measuring this unclipped inner wrapper's natural height and
  // reporting it up lets the parent size the row to fit real content instead of
  // guessing from message length or status.
  useLayoutEffect(() => {
    const node = contentRef.current;
    if (!node || !onHeightChange) {
      return undefined;
    }

    const reportHeight = () =>
      onHeightChange(node.getBoundingClientRect().height);
    reportHeight();

    const observer = new ResizeObserver(reportHeight);
    observer.observe(node);
    return () => observer.disconnect();
  }, [onHeightChange, expand, type, did]);

  const handleViewFilesClick = (
    e: React.MouseEvent<HTMLDivElement, MouseEvent>
  ) => {
    e.stopPropagation();
  };

  return (
    <div className={classes.listItemContainer} style={style}>
      <div ref={contentRef}>
        <div
          className={
            expand ? classes.listItemExpanded : classes.listItemCollapsed
          }
          onClick={onClick}
        >
          <div className={classes.iconContainer}>
            {type === 'file' && (
              <i className={`${classes.fileIcon} material-icons`}>attachment</i>
            )}
            {type === 'container' && (
              <i className={`${classes.containerIcon} material-icons`}>
                folder
              </i>
            )}
            {type === 'dataset' && (
              <i className={`${classes.datasetIcon} material-icons`}>
                folder_open
              </i>
            )}
          </div>
          <div className={classes.textContainer}>{did}</div>
          {type === 'file' && !!size && (
            <div className={classes.sizeContainer}>
              {toHumanReadableSize(size)}
            </div>
          )}
          {(type === 'container' || type === 'dataset') && (
            <div onClick={handleViewFilesClick}>
              <ListAttachedFilesPopover did={did}>
                <i className={`${classes.listFilesIcon} material-icons`}>
                  visibility
                </i>
              </ListAttachedFilesPopover>
            </div>
          )}
        </div>
        {!!expand && type === 'file' && <FileDIDItemDetails did={did} />}
        {!!expand && (type === 'container' || type === 'dataset') && (
          <CollectionDIDItemDetails did={did} />
        )}
      </div>
    </div>
  );
};
