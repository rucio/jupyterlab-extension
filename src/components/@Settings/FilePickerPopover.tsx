import React, { useState, useEffect, useCallback } from 'react';
import { createUseStyles } from 'react-jss';
import { FixedSizeList } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import Popover from 'react-popover';
import { withRequestAPI, WithRequestAPIProps } from '../../utils/Actions';
import { DirectoryItem } from '../../types';

const useStyles = createUseStyles({
  main: {
    width: '300px'
  },
  heading: {
    background: '#efefef',
    color: '#808080',
    padding: '8px',
    borderBottom: '1px solid #e0e0e0',
    fontSize: '9pt'
  },
  content: {
    fontSize: '10pt',
    overflow: 'auto',
    height: '250px',
    '&.loading': {
      opacity: 0.4,
      pointerEvents: 'none'
    }
  },
  icon: {
    fontSize: '16px',
    verticalAlign: 'middle'
  },
  clickable: {
    cursor: 'pointer'
  },
  folderName: {
    verticalAlign: 'middle'
  },
  listItem: {
    display: 'flex',
    padding: '8px',
    borderBottom: '1px solid #E0E0E0',
    flexDirection: 'row',
    fontSize: '9pt',
    cursor: 'pointer',
    alignItems: 'center',
    boxSizing: 'border-box',
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
  fileIcon: {
    extend: 'icon',
    color: '#66B100'
  },
  dirIcon: {
    extend: 'icon',
    color: '#5DC0FD'
  }
});

interface FilePickerPopoverProps {
  onFilePicked: { (path: string): void };
}

type MyProps = React.HTMLAttributes<HTMLDivElement> & FilePickerPopoverProps;

const _FilePickerPopover: React.FC<MyProps> = ({ children, onFilePicked, ...props }) => {
  const { actions } = props as WithRequestAPIProps;

  const classes = useStyles();
  const [path, setPath] = useState<string[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [directoryItems, setDirectoryItems] = useState<DirectoryItem[]>([]);
  const [itemsCache, setItemsCache] = useState<{ [path: string]: DirectoryItem[] }>({});

  const openPopover = () => {
    setOpen(true);
    setPath([]);
    setDirectoryItems([]);
    setItemsCache({});
  };

  const itemsSortFunction = (a: DirectoryItem, b: DirectoryItem): number => {
    if (a.type === b.type) {
      return a.name.toLowerCase() < b.name.toLowerCase() ? -1 : 1;
    }
    return a.type === 'dir' && b.type === 'file' ? -1 : 1;
  };

  const loadDirectoryItem = () => {
    const pathString = path.join('/');
    if (itemsCache[pathString]) {
      setDirectoryItems(itemsCache[pathString]);
    } else {
      setLoading(true);
      actions
        .listDirectory(pathString)
        .then(items => items.sort(itemsSortFunction))
        .then(items => {
          const newItemsCache = { ...itemsCache };
          newItemsCache[pathString] = items;
          setItemsCache(newItemsCache);
          setDirectoryItems(items);
        })
        .catch(() => setDirectoryItems([]))
        .finally(() => {
          setLoading(false);
        });
    }
  };

  useEffect(loadDirectoryItem, [path]);

  const moveToUpperDirectory = () => {
    const newPath = path.filter((p, i) => {
      return i < path.length - 1;
    });
    setPath(newPath);
  };

  const moveToHomeDirectory = () => {
    setPath([]);
  };

  const onKeyDown = useCallback(event => {
    if (event.keyCode === 27) {
      setOpen(false);
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', onKeyDown, false);

    return () => {
      document.removeEventListener('keydown', onKeyDown, false);
    };
  }, []);

  const onItemClick = (item: DirectoryItem) => {
    if (item.type === 'dir') {
      setPath([...path, item.name]);
    } else {
      onFilePicked(item.path);
      setOpen(false);
    }
  };

  const Row = ({ index, style }: any) => {
    const item = directoryItems[index];
    return <ListItem style={style} directoryItem={item} key={item.path} onClick={() => onItemClick(item)} />;
  };

  const popoverBody = (
    <div className={classes.main}>
      <div className={classes.heading}>
        <span className={`material-icons ${classes.icon} ${classes.clickable}`} onClick={moveToHomeDirectory}>
          home
        </span>
        {path.length === 0 && <span className={classes.folderName}>&nbsp; Home</span>}
        {path.length >= 1 && <span className={`material-icons ${classes.icon}`}>navigate_next</span>}
        {path.length >= 2 && (
          <>
            <span className={`material-icons ${classes.icon} ${classes.clickable}`} onClick={moveToUpperDirectory}>
              more_horiz
            </span>
            <span className={`material-icons ${classes.icon}`}>navigate_next</span>
          </>
        )}
        <span className={classes.folderName}>{path ? path[path.length - 1] : ''}</span>
      </div>
      <div className={`${classes.content} ${loading ? 'loading' : ''}`}>
        <AutoSizer>
          {({ height, width }) => (
            <FixedSizeList height={height} itemCount={directoryItems.length} itemSize={32} width={width}>
              {Row}
            </FixedSizeList>
          )}
        </AutoSizer>
      </div>
    </div>
  );

  return (
    <Popover
      enterExitTransitionDurationMs={0}
      isOpen={open}
      preferPlace="above"
      body={popoverBody}
      onOuterAction={() => setOpen(false)}
    >
      <div onClick={openPopover}>{children}</div>
    </Popover>
  );
};

const ListItem: React.FC<{ directoryItem: DirectoryItem; onClick: { (): void }; style: any }> = ({
  directoryItem,
  onClick,
  style
}) => {
  const classes = useStyles();

  return (
    <div className={classes.listItem} onClick={onClick} style={style}>
      <div className={classes.iconContainer}>
        {directoryItem.type === 'file' && <i className={`${classes.fileIcon} material-icons`}>attachment</i>}
        {directoryItem.type === 'dir' && <i className={`${classes.dirIcon} material-icons`}>folder</i>}
      </div>
      <div className={classes.textContainer}>{directoryItem.name}</div>
    </div>
  );
};

export const FilePickerPopover = withRequestAPI(_FilePickerPopover);
