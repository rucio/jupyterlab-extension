import React, { useEffect, useState } from 'react';
import { createUseStyles } from 'react-jss';
import EventBus from '../utils/EventBus';

const useStyles = createUseStyles({
  container: {
    padding: '16px'
  }
});

export const Notebook: React.FunctionComponent = () => {
  const classes = useStyles();
  const [activeModel, setActiveModel] = useState<any>();

  useEffect(() => {
    const unsubscribe = EventBus.activeNotebook.on(notebookPanel => {
      if (notebookPanel) {
        console.log('Notebook active');
        notebookPanel.revealed.then(() => {
          setActiveModel(notebookPanel.content.model.metadata.toJSON());
        });
      } else {
        setActiveModel(undefined);
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  return (
    <div className={classes.container}>
      {!!activeModel && JSON.stringify(activeModel)}
    </div>
  );
};
