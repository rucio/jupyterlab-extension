import React from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../stores/ExtensionStore';
import { NotebookAttachmentListItem } from '../components/@Notebook/NotebookAttachmentListItem';
import { HorizontalHeading } from '../components/HorizontalHeading';

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

  return (
    <>
      {!!activeNotebookPanel && !!activeNotebookAttachments && activeNotebookAttachments.length > 0 && (
        <div className={classes.container}>
          {activeNotebookAttachments.length > 0 && (
            <>
              <HorizontalHeading title="Attached DIDs" />
              {activeNotebookAttachments.map((attachment, i) => (
                <NotebookAttachmentListItem key={i} attachment={attachment} />
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
