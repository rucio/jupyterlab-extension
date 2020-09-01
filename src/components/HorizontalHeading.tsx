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
  heading: {
    borderBottom: '1px solid var(--jp-border-color2)',
    margin: 0,
    padding: '24px 16px 8px 16px',
    fontWeight: 'bold',
    textAlign: 'start',
    fontSize: '9pt',
    textTransform: 'uppercase'
  }
});

interface HorizontalHeadingProps {
  title: string;
}

export const HorizontalHeading: React.FC<HorizontalHeadingProps> = ({ title }) => {
  const classes = useStyles();
  return <div className={classes.heading}>{title}</div>;
};
