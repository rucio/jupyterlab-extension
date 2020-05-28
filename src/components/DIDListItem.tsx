import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  listItem: {
    display: 'flex',
    flexDirection: 'row',
    fontSize: '9pt',
    alignItems: 'stretch',
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
  },
  textContainer: {
    flex: 1,
    textOverflow: 'ellipsis',
    overflow: 'hidden'
  },
  iconContainer: {
    lineHeight: 0,
    marginRight: '8px'
  },
  icon: {
    fontSize: '16px'
  },
  fileIcon: {
    extend: 'icon',
    color: '#66B100'
  },
  containerIcon: {
    extend: 'icon',
    color: '#5DC0FD'
  },
  datasetIcon: {
    extend: 'icon',
    color: '#FFB100'
  },
  starActiveIcon: {
    color: '#ffd600'
  },
  starInactiveIcon: {
    color: '#E0E0E0'
  }
});

export interface DIDItem {
  type: string;
  did: string;
  onClick?: { (): void };
}

export const DIDListItem: React.FC<DIDItem> = ({ type, did, onClick }) => {
  const classes = useStyles();

  const icon = (() => {
    switch (type) {
      case 'file':
        return (
          <i className={`${classes.fileIcon} material-icons`}>attachment</i>
        );
      case 'dataset':
        return (
          <i className={`${classes.datasetIcon} material-icons`}>folder_open</i>
        );
      case 'container':
        return (
          <i className={`${classes.containerIcon} material-icons`}>folder</i>
        );
      default:
        return <i>&nbsp;</i>;
    }
  })();

  return (
    <div className={classes.listItem} onClick={onClick}>
      <div className={classes.iconContainer}>{icon}</div>
      <div className={classes.textContainer}>{did}</div>
    </div>
  );
};
