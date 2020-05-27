import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';
import { settingsIcon } from '@jupyterlab/ui-components';

import { Header } from '../components/Header';
import { MenuBar } from '../components/MenuBar';
import { Settings } from './pages/Settings';
import { Explore } from './pages/Explore';
import { MyDatasets } from './pages/MyDatasets';

const useStyles = createUseStyles({
  menuBar: {
    marginTop: '16px'
  }
});

const menus = [
  { title: 'Explore', value: 1, right: false },
  { title: 'My Datasets', value: 2, right: false },
  {
    title: (
      <div style={{ lineHeight: '1px' }}>
        <settingsIcon.react tag="div" height="16px" />
      </div>
    ),
    value: 3,
    right: true
  }
];

export const Panel: React.FunctionComponent = () => {
  const classes = useStyles();
  const [activeMenu, setActiveMenu] = useState(1);

  return (
    <div>
      <Header />
      <div className={classes.menuBar}>
        <MenuBar
          menus={menus}
          value={activeMenu}
          onChange={(value: any) => setActiveMenu(value)}
        />
      </div>
      <div>
        {activeMenu === 1 && <Explore />}
        {activeMenu === 2 && <MyDatasets />}
        {activeMenu === 3 && <Settings />}
      </div>
    </div>
  );
};
