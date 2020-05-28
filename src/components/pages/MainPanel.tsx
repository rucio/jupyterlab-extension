import React from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../../ExtensionStore';
import { MenuBar } from '../MenuBar';
import { Explore } from '../tabs/Explore';
import { Bookmarks } from '../tabs/Bookmarks';
import { Info } from '../tabs/Info';

const useStyles = createUseStyles({
  container: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'auto'
  },
  menuBar: {
    marginTop: '16px'
  },
  content: {
    flex: 1,
    overflow: 'auto'
  },
  instanceOption: {
    lineHeight: 0
  },
  infoIcon: {
    fontSize: '15px'
  }
});

export const MainPanel: React.FC<React.HTMLAttributes<HTMLElement>> = props => {
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
        <div className={classes.instanceOption}>
          <i className={`${classes.infoIcon} material-icons`}>info</i>
        </div>
      ),
      value: 3,
      right: true
    }
  ];

  return (
    <div className={classes.container} {...props}>
      <div className={classes.menuBar}>
        <MenuBar menus={menus} value={activeMenu} onChange={setActiveMenu} />
      </div>
      <div className={classes.content}>
        {activeMenu === 1 && <Explore />}
        {activeMenu === 2 && <Bookmarks />}
        {activeMenu === 3 && <Info />}
      </div>
    </div>
  );
};
