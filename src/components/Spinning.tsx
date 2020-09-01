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
  '@keyframes rotation': {
    from: {
      transform: 'rotate(0deg)'
    },
    to: {
      transform: 'rotate(359deg)'
    }
  },
  rotate: {
    animation: '$rotation 1s infinite linear',
    animationName: '$rotation'
  }
});

export const Spinning: React.FC<React.HTMLAttributes<HTMLElement>> = ({ children, className, ...props }) => {
  const classes = useStyles();
  return (
    <span className={`${className} ${classes.rotate}`} {...props}>
      {children}
    </span>
  );
};
