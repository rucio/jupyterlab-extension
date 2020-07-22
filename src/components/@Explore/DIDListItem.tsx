import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';
import { FileDIDItemDetails } from './FileDIDItemDetails';
import { ContainerDIDItemDetails } from './ContainerDIDItemDetails';
import { toHumanReadableSize } from '../../utils/Helpers';

const useStyles = createUseStyles({
  listItemContainer: {
    borderBottom: '1px solid #E0E0E0'
  },
  listItem: {
    display: 'flex',
    flexDirection: 'row',
    fontSize: '9pt',
    alignItems: 'stretch',
    padding: '8px 16px 8px 16px',
    cursor: 'pointer'
  },
  listItemCollapsed: {
    extend: 'listItem',
    '&:hover': {
      backgroundColor: '#eeeeee'
    }
  },
  listItemExpanded: {
    extend: 'listItem',
    backgroundColor: '#F8F8F8'
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
  sizeContainer: {
    color: '#808080'
  }
});

export interface DIDItem {
  did: string;
  size?: number;
  type: 'dataset' | 'container' | 'file';
  onClick?: { (): boolean | undefined };
  expand?: boolean;
}

export const DIDListItem: React.FC<DIDItem> = ({ did, size, type, onClick, expand }) => {
  const classes = useStyles();
  const [open, setOpen] = useState(expand);

  const handleItemClick = () => {
    if (onClick) {
      if (!onClick()) {
        return;
      }
    }

    setOpen(!open);
  };

  return (
    <div className={classes.listItemContainer}>
      <div className={open ? classes.listItemExpanded : classes.listItemCollapsed} onClick={handleItemClick}>
        <div className={classes.iconContainer}>
          {type === 'file' && <i className={`${classes.fileIcon} material-icons`}>attachment</i>}
          {type === 'container' && <i className={`${classes.containerIcon} material-icons`}>folder</i>}
          {type === 'dataset' && <i className={`${classes.datasetIcon} material-icons`}>folder_open</i>}
        </div>
        <div className={classes.textContainer}>{did}</div>
        {!!size && <div className={classes.sizeContainer}>{toHumanReadableSize(size)}</div>}
      </div>
      {!!open && type === 'file' && <FileDIDItemDetails did={did} />}
      {!!open && (type === 'container' || type === 'dataset') && <ContainerDIDItemDetails did={did} />}
    </div>
  );
};
