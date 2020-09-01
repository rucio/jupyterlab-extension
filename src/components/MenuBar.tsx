/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
 */

import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  tab: {
    borderBottom: '1px solid var(--jp-border-color2)',
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
      background: 'var(--jp-layout-color2)'
    },
    '&.active': {
      background: 'var(--jp-layout-color2)',
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
