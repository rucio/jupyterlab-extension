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

export const Spinning: React.FC<React.HTMLAttributes<HTMLElement>> = ({
  children,
  className,
  ...props
}) => {
  const classes = useStyles();
  return (
    <span className={`${className} ${classes.rotate}`} {...props}>
      {children}
    </span>
  );
};
