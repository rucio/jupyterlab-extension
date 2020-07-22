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
    backgroundColor: '#FFFFFF',
    boxShadow: '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
    borderRadius: '4px',
    zIndex: 1,
    fontSize: '10pt'
  },
  dropdownActive: {
    minWidth: (props: InlineDropdownProps) => props.optionWidth || '150px',
    extend: 'dropdownContent',
    display: 'block'
  },
  dropdownListItem: {
    padding: '8px',
    width: 'auto',
    borderBottom: '1px solid #e0e0e0',
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: '#2196F3',
      color: '#ffffff'
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
  const clickTargetRef = useRef<HTMLElement>();

  const handleClickOutside = (event: Event) => {
    if (clickTargetRef && !clickTargetRef.current.contains(event.target as Node)) {
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
        &nbsp;
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
