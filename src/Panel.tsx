import React from 'react';
import { useStoreState } from 'pullstate';
import { createUseStyles } from 'react-jss';
import { ExtensionStore } from './stores/ExtensionStore';
import { Header } from './components/Header';
import { MainPanel } from './pages/MainPanel';
import { SelectInstance } from './pages/SelectInstance';

const useStyles = createUseStyles({
  panel: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  },
  section: {
    flex: 1
  }
});

export const Panel: React.FunctionComponent = () => {
  const classes = useStyles();
  const activeInstance = useStoreState(ExtensionStore, s => s.activeInstance);

  const instances = [
    { displayName: 'ATLAS', value: 'atlas' },
    { displayName: 'ALICE', value: 'alice' },
    { displayName: 'LHCb', value: 'lhcb' },
    { displayName: 'CMS', value: 'cms' }
  ];

  const setActiveInstance = (value?: string) => {
    ExtensionStore.update(s => {
      const instance = instances.find(i => i.value === value);
      s.activeInstance = instance;
    });
  };

  return (
    <div className={classes.panel}>
      <Header />
      {!!activeInstance && <MainPanel />}
      {!activeInstance && (
        <SelectInstance
          instances={instances}
          onSelectInstance={setActiveInstance}
        />
      )}
    </div>
  );
};
