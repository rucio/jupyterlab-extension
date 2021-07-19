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
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../stores/ExtensionStore';
import { NotebookAttachmentListItem } from '../components/@Notebook/NotebookAttachmentListItem';
import { HorizontalHeading } from '../components/HorizontalHeading';
import { useNotebookResolveStatusStore } from '../utils/NotebookListener';

const useStyles = createUseStyles({
  container: {
    padding: '16px 0 16px 0'
  },
  messageContainer: {
    padding: '16px'
  }
});

export const Notebook: React.FunctionComponent = () => {
  const classes = useStyles();
  const activeNotebookPanel = useStoreState(ExtensionStore, s => s.activeNotebookPanel);
  const activeNotebookAttachments = useStoreState(ExtensionStore, s => s.activeNotebookAttachment);
  const notebookStatusStore = useNotebookResolveStatusStore();
  const notebookStatus = activeNotebookPanel?.id ? notebookStatusStore[activeNotebookPanel?.id] : null;

  return (
    <>
      {!!activeNotebookPanel && !!activeNotebookAttachments && activeNotebookAttachments.length > 0 && (
        <div className={classes.container}>
          {activeNotebookAttachments.length > 0 && (
            <>
              <HorizontalHeading title="Attached DIDs" />
              {activeNotebookAttachments.map(attachment => (
                <NotebookAttachmentListItem
                  key={attachment.did}
                  attachment={attachment}
                  status={notebookStatus ? notebookStatus[attachment.did] : undefined}
                />
              ))}
            </>
          )}
        </div>
      )}
      {!!activeNotebookPanel && !!activeNotebookAttachments && activeNotebookAttachments.length === 0 && (
        <div className={classes.messageContainer}>
          You have not attached any DID. Use the Explore menu to add a DID to this notebook.
        </div>
      )}
      {!activeNotebookPanel && <div className={classes.messageContainer}>Please open a Notebook.</div>}
    </>
  );
};
