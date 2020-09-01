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
  control: {
    display: 'flex',
    flexDirection: 'row',
    border: (props: TextFieldProps) => `1px solid ${props.outlineColor || 'var(--jp-border-color1)'}`,
    alignItems: 'stretch'
  },
  input: {
    flex: 1,
    background: 'none',
    border: 'none',
    outline: 'none',
    padding: '8px',
    minWidth: 0,
    color: (props: TextFieldProps) => props.color || 'var(--jp-ui-font-color1)'
  },
  block: {
    width: '100%'
  }
});

interface TextFieldProps {
  outlineColor?: string;
  color?: string;
  block?: boolean;
  before?: any;
  after?: any;
}

type MyProps = TextFieldProps & React.InputHTMLAttributes<HTMLInputElement>;

const _TextField = (props: MyProps, ref: React.Ref<HTMLInputElement>) => {
  const { block, before, after, outlineColor, className, ...carriedProps } = props;
  const classes = useStyles({ outlineColor });

  const inputClasses = [classes.input];
  if (block) {
    inputClasses.push(classes.block);
  }
  return (
    <div className={classes.control}>
      {before}
      <input ref={ref} type="text" className={inputClasses.join(' ') + ' ' + className || ''} {...carriedProps} />
      {after}
    </div>
  );
};

export const TextField = React.forwardRef(_TextField);
