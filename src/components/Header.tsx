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
import RucioLogo from './RucioLogo';

const useStyles = createUseStyles({
  container: {
    padding: '16px 8px 8px 8px'
  }
});

export const Header: React.FunctionComponent<React.HTMLAttributes<HTMLElement>> = props => {
  const classes = useStyles();

  return (
    <div className={classes.container} {...props}>
      <RucioLogo />
    </div>
  );
};
