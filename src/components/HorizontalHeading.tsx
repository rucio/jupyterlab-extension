import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  heading: {
    borderBottom: '1px solid #e0e0e0',
    margin: 0,
    padding: '24px 8px 8px 8px',
    fontWeight: 'bold',
    textAlign: 'start',
    fontSize: '10pt',
    textTransform: 'uppercase'
  }
});

interface HorizontalHeadingProps {
  title: string;
}

export const HorizontalHeading: React.FC<HorizontalHeadingProps> = ({
  title
}) => {
  const classes = useStyles();
  return <div className={classes.heading}>{title}</div>;
};
