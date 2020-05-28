import React, { useState } from 'react';

import { Header } from '../components/Header';
import { MainPanel } from './pages/MainPanel';
import { SelectInstance } from './pages/SelectInstance';

export const Panel: React.FunctionComponent = () => {
  const [activeInstance] = useState();
  const instances = [
    { displayName: 'ATLAS', value: 'atlas' },
    { displayName: 'ALICE', value: 'alice' },
    { displayName: 'LHCb', value: 'lhcb' },
    { displayName: 'CMS', value: 'cms' }
  ];

  return (
    <div>
      <Header />
      {!!activeInstance && <MainPanel />}
      {!activeInstance && <SelectInstance instances={instances} />}
    </div>
  );
};
