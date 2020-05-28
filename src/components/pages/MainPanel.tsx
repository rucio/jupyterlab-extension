import React from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../../ExtensionStore';
import { MenuBar } from '../MenuBar';
import { Explore } from '../tabs/Explore';
import { Bookmarks } from '../tabs/Bookmarks';
import { Info } from '../tabs/Info';

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
  const classes = useStyles();
  const activeMenu = useStoreState(ExtensionStore, s => s.activeMenu);
  const setActiveMenu = (value?: any) => {
    ExtensionStore.update(s => {
      s.activeMenu = value;
    });
  };
  const menus = [
    { title: 'Explore', value: 1, right: false },
    { title: 'Bookmarks', value: 2, right: false },
    {
      title: (
        <div className={`${classes.instanceOption} jp-icon-info`}>&nbsp;</div>
      ),
      value: 3,
      right: true
    }
  ];

  return (
    <>
      <div className={classes.menuBar}>
        <MenuBar menus={menus} value={activeMenu} onChange={setActiveMenu} />
      </div>
      <div>
        {activeMenu === 1 && <Explore />}
        {activeMenu === 2 && <Bookmarks />}
        {activeMenu === 3 && <Info />}
      </div>
    </>
  );
};
