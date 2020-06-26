import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { UIStore } from '../stores/UIStore';
import { MenuBar } from '../components/MenuBar';
import { Explore } from '../tabs/Explore';
import { Notebook } from '../tabs/Notebook';
import { Settings } from '../tabs/Settings';

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
  },
  hidden: {
    display: 'none'
  }
});

export const MainPanel: React.FC<React.HTMLAttributes<HTMLElement>> = props => {
  const classes = useStyles();
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const [activeMenu, setActiveMenu] = useState(activeInstance ? 1 : 3);
  const menus = [
    { title: 'Explore', value: 1, right: false, disabled: !activeInstance },
    { title: 'Notebook', value: 2, right: false, disabled: !activeInstance },
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
        <div className={activeMenu !== 1 ? classes.hidden : ''}>{activeInstance && <Explore />}</div>
        <div className={activeMenu !== 2 ? classes.hidden : ''}>{activeInstance && <Notebook />}</div>
        <div className={activeMenu !== 3 ? classes.hidden : ''}>
          <Settings />
        </div>
      </div>
    </div>
  );
};
