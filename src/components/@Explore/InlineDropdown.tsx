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

import React, { useState, useEffect, useRef } from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  dropdown: {
    position: 'relative',
    display: 'inline-block'
  },
  dropdownTitle: {
    cursor: 'pointer'
  },
  dropdownContent: {
    display: 'none',
    position: 'absolute',
    marginTop: '8px',
    boxShadow: '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
    borderRadius: '4px',
    zIndex: 1,
    fontSize: '10pt',
    background: 'var(--jp-layout-color1)',
    color: 'var(--jp-ui-font-color1)'
  },
  dropdownActive: {
    minWidth: (props: Partial<InlineDropdownProps>) => props.optionWidth || '150px',
    extend: 'dropdownContent',
    display: 'block'
  },
  dropdownListItem: {
    padding: '8px',
    width: 'auto',
    borderBottom: '1px solid var(--jp-border-color2)',
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: 'var(--jp-layout-color2)'
    },
    '&:last-child': {
      borderBottom: 'none'
    }
  },
  icon: {
    fontSize: '16px',
    verticalAlign: 'middle'
  }
});

interface Option {
  title: string;
  value: any;
}

interface InlineDropdownProps {
  options: Option[];
  value: any;
  onItemSelected?: { (value: any): void };
  optionWidth?: string;
}

type MyProps = React.HTMLAttributes<HTMLSpanElement> & InlineDropdownProps;

export const InlineDropdown: React.FC<MyProps> = ({ options, value, onItemSelected, optionWidth, ...props }) => {
  const classes = useStyles({ optionWidth });
  const [open, setOpen] = useState(false);
  const currentOption = options.find(o => o.value === value);
  const clickTargetRef = useRef<HTMLElement>(null);

  const handleClickOutside = (event: Event) => {
    if (clickTargetRef && !clickTargetRef.current?.contains(event.target as Node)) {
      setOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  });

  return (
    <span className={classes.dropdown} onClick={() => setOpen(!open)} ref={clickTargetRef}>
      <span className={classes.dropdownTitle} {...props}>
        {currentOption ? currentOption.title : '(select)'}
        <span className={`${classes.icon} material-icons`}>arrow_drop_down</span>
      </span>
      <div className={open ? classes.dropdownActive : classes.dropdownContent}>
        {options.map(option => (
          <div
            className={classes.dropdownListItem}
            onClick={() => onItemSelected && onItemSelected(option.value)}
            key={option.value}
          >
            {option.title}
          </div>
        ))}
      </div>
    </span>
  );
};
