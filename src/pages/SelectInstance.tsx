import React from 'react';
import { createUseStyles } from 'react-jss';
import { Instance } from '../types';

const useStyles = createUseStyles({
  container: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'auto'
  },
  title: {
    margin: '0 0 4px 0'
  },
  subtitle: {
    color: '#808080'
  },
  heading: {
    marginBottom: '8px',
    padding: '16px'
  },
  listContainer: {
    flex: 1,
    overflow: 'auto'
  },
  listItem: {
    borderBottom: '1px solid #E0E0E0',
    padding: '8px 16px 8px 16px',
    cursor: 'pointer',
    'background-size': 'auto 50%',
    'background-position': 'right 16px center',
    backgroundRepeat: 'no-repeat',
    '&:last-child': {
      borderBottom: 'none'
    },
    '&:hover': {
      backgroundColor: '#eeeeee'
    }
  }
});

interface SelectInstanceProps {
  instances: Instance[];
  onSelectInstance: { (value: string): void };
}

type MyProps = SelectInstanceProps & React.HTMLAttributes<HTMLElement>;

export const SelectInstance: React.FC<MyProps> = ({
  instances,
  onSelectInstance,
  ...props
}) => {
  const classes = useStyles();

  return (
    <div className={classes.container} {...props}>
      <div className={classes.heading}>
        <h2 className={classes.title}>Select an Instance</h2>
        <p className={classes.subtitle}>
          Select one of the instances relevant to your experiment.
        </p>
      </div>
      <div className={classes.listContainer}>
        {instances.map(instance => (
          <div
            key={instance.value}
            className={`${classes.listItem} jp-icon-arrow-right`}
            onClick={() => onSelectInstance(instance.value)}
          >
            {instance.displayName}
          </div>
        ))}
      </div>
    </div>
  );
};
