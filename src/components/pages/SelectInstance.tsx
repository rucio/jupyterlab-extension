import React from 'react';
import { createUseStyles } from 'react-jss';
import { Instance } from '../../types';

const useStyles = createUseStyles({
  container: {},
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
  listItem: {
    borderBottom: '1px solid #ddd',
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
  onSelect: { (value: string): void };
}

export const SelectInstance: React.FC<SelectInstanceProps> = ({
  instances,
  onSelect
}) => {
  const classes = useStyles();

  return (
    <div className={classes.container}>
      <div className={classes.heading}>
        <h2 className={classes.title}>Select an Instance</h2>
        <p className={classes.subtitle}>
          Select one of the instances relevant to your experiment.
        </p>
      </div>
      <div>
        {instances.map(instance => (
          <div
            key={instance.value}
            className={`${classes.listItem} jp-icon-arrow-right`}
            onClick={() => onSelect(instance.value)}
          >
            {instance.displayName}
          </div>
        ))}
      </div>
    </div>
  );
};
