import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  tab: {
    borderBottom: '1px solid #e0e0e0',
    listStyleType: 'none',
    margin: 0,
    padding: '0 8px 0 8px',
    overflow: 'hidden'
  },
  tabItem: {
    float: 'left',
    display: 'block',
    padding: '8px 12px 8px 12px',
    textTransform: 'uppercase',
    borderRadius: '4px 4px 0 0',
    fontSize: '9pt',
    cursor: 'pointer',
    '&:hover': {
      background: '#f9f9f9'
    },
    '&.active': {
      background: '#f0f0f0',
      fontWeight: 'bold'
    },
    '&.disabled': {
      opacity: 0.5,
      cursor: 'inherit',
      '&:hover': {
        background: 'none'
      },
      '&.active': {
        background: 'none'
      }
    }
  },
  tabItemRight: {
    extend: 'tabItem',
    float: 'right'
  }
});

interface MenuBarProps {
  value?: any;
  onChange: { (value: any): void };
  menus: Menu[];
}

export interface Menu {
  title: any;
  value: any;
  right?: boolean;
  disabled?: boolean;
}

export const MenuBar: React.FunctionComponent<MenuBarProps> = ({ menus, value, onChange }) => {
  const classes = useStyles();

  return (
    <div>
      <ul className={classes.tab}>
        {menus.map(menu => {
          const activeClass = menu.value === value ? 'active' : '';
          const disabledClass = menu.disabled ? 'disabled' : '';
          const tabClass = menu.right ? classes.tabItemRight : classes.tabItem;
          return (
            <li
              onClick={!menu.disabled ? () => onChange(menu.value) : undefined}
              key={menu.value}
              className={`${tabClass} ${activeClass} ${disabledClass}`}
            >
              {menu.title}
            </li>
          );
        })}
      </ul>
    </div>
  );
};
