import React from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../stores/ExtensionStore';
import { NotebookDIDAttachment } from '../types';

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
  const setActiveNotebookAttachments = (
    attachments: NotebookDIDAttachment[]
  ) => {
    ExtensionStore.update(s => {
      s.activeNotebookAttachment = attachments;
    });
  };

  const addAttachment = () => {
    const attachment: NotebookDIDAttachment = {
      did: 'test:f2',
      type: 'container',
      variableName: 'coolme'
    };

    const notebookAttachments = activeNotebookAttachments
      ? [...activeNotebookAttachments, attachment]
      : [attachment];
    setActiveNotebookAttachments(notebookAttachments);
  };

  return (
    <div className={classes.container}>
      {!!activeNotebookPanel &&
        !!activeNotebookAttachments &&
        activeNotebookAttachments.map((attachment, i) => (
          <div key={i}>
            {attachment.did} {attachment.variableName}
          </div>
        ))}

      <button type="button" onClick={addAttachment}>
        Add new attachment
      </button>
    </div>
  );
};
