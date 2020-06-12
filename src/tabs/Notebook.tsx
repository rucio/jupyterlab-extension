import React from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../stores/ExtensionStore';

const useStyles = createUseStyles({
  container: {
    padding: '16px'
  }
});

export const Notebook: React.FunctionComponent = () => {
  const classes = useStyles();
  const activeNotebookPanel = useStoreState(
    ExtensionStore,
    s => s.activeNotebookPanel
  );
  const activeNotebookAttachments = useStoreState(
    ExtensionStore,
    s => s.activeNotebookAttachment
  );

  return (
    <div className={classes.container}>
      {!!activeNotebookPanel &&
        !!activeNotebookAttachments &&
        activeNotebookAttachments.map((attachment, i) => (
          <div key={i}>
            {attachment.did} {attachment.variableName}
          </div>
        ))}
    </div>
  );
};
