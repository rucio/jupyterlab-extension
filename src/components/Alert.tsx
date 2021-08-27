import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  root: {
    padding: '8px',
    border: '1px solid var(--jp-warn-color1)',
    // backgroundColor: 'var(--jp-warn-color1)',
    color: 'var(--jp-warn-color1)',
    borderRadius: '4px',
    maxWidth: '400px',
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center'
  },
  icon: {
    color: 'var(--jp-warn-color1)'
  },
  textContainer: {
    flex: 1,
    paddingLeft: '8px'
  }
});

type MyProps = {
  children?: React.ReactNode;
} & React.HTMLAttributes<HTMLDivElement>;

export const Alert: React.FC<MyProps> = ({ children, ...props }) => {
  const classes = useStyles();
  return (
    <div className={classes.root} {...props}>
      <div>
        <i className={`material-icons ${classes.icon}`}>warning</i>
      </div>
      <div className={classes.textContainer}>{children}</div>
    </div>
  );
};
