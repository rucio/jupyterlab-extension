import React from 'react';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../ExtensionStore';
import { Header } from '../components/Header';
import { MainPanel } from './pages/MainPanel';
import { SelectInstance } from './pages/SelectInstance';

export const Panel: React.FunctionComponent = () => {
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
    <div>
      <Header />
      {!!activeInstance && <MainPanel />}
      {!activeInstance && (
        <SelectInstance instances={instances} onSelect={setActiveInstance} />
      )}
    </div>
  );
};
