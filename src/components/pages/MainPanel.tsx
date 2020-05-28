import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';

import { MenuBar } from '../MenuBar';
import { Explore } from '../tabs/Explore';
import { MyDatasets } from '../tabs/MyDatasets';

const useStyles = createUseStyles({
  menuBar: {
    marginTop: '16px'
  },
  instanceOption: {
    width: '16px',
    backgroundSize: '100%',
    backgroundRepeat: 'no-repeat'
  }
});

export const MainPanel: React.FC = () => {
  const [activeMenu, setActiveMenu] = useState(1);
  const classes = useStyles();

  const menus = [
    { title: 'Explore', value: 1, right: false },
    { title: 'My Datasets', value: 2, right: false },
    {
      title: (
        <div className={`${classes.instanceOption} jp-icon-swap`}>&nbsp;</div>
      ),
      value: 3,
      right: true
    }
  ];

  return (
    <>
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
      </div>
    </>
  );
};
