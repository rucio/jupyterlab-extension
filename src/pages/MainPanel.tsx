import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';
import { MenuBar } from '../components/MenuBar';
import { Explore } from '../tabs/Explore';
import { Notebook } from '../tabs/Notebook';
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
  },
  hidden: {
    display: 'none'
  }
});

export const MainPanel: React.FC<React.HTMLAttributes<HTMLElement>> = props => {
  const classes = useStyles();
  const [activeMenu, setActiveMenu] = useState(1);
  const menus = [
    { title: 'Explore', value: 1, right: false },
    { title: 'Notebook', value: 2, right: false },
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
        <div className={activeMenu !== 1 ? classes.hidden : ''}>
          <Explore />
        </div>
        <div className={activeMenu !== 2 ? classes.hidden : ''}>
          <Notebook />
        </div>
        <div className={activeMenu !== 3 ? classes.hidden : ''}>
          <Info />
        </div>
      </div>
    </div>
  );
};
