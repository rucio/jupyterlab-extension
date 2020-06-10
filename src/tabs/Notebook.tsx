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

  return (
    <div className={classes.container}>
      {!!activeNotebookPanel &&
        JSON.stringify(activeNotebookPanel.model.metadata.toJSON())}
    </div>
  );
};
