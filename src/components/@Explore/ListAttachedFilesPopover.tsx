import React, { useState, useEffect, useCallback } from 'react';
import Popover from 'react-popover';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { UIStore } from '../../stores/UIStore';
import { AttachedFile } from '../../types';
import { actions } from '../../utils/Actions';
import { DIDListItem } from './DIDListItem';
import { Spinning } from '../Spinning';

const useStyles = createUseStyles({
  main: {
    width: '300px'
  },
  heading: {
    background: '#efefef',
    color: '#808080',
    padding: '8px',
    borderBottom: '1px solid #e0e0e0',
    fontSize: '9pt',
    display: 'flex',
    flexDirection: 'row'
  },
  headingText: {
    textOverflow: 'ellipsis',
    overflow: 'hidden',
    flex: 1
  },
  content: {
    fontSize: '10pt',
    overflow: 'auto',
    maxHeight: '250px',
    '&.loading': {
      opacity: 0.4,
      pointerEvents: 'none'
    }
  },
  loading: {
    padding: '8px'
  },
  icon: {
    fontSize: '16px',
    verticalAlign: 'middle'
  },
  iconText: {
    fontSize: '9pt',
    verticalAlign: 'middle',
    paddingLeft: '4px'
  },
  headingCloseButton: {
    extend: 'icon',
    cursor: 'pointer'
  }
});

interface ListAttachedFilesPopoverProps {
  did: string;
}

type MyProps = React.HTMLAttributes<HTMLDivElement> & ListAttachedFilesPopoverProps;

export const ListAttachedFilesPopover: React.FC<MyProps> = ({ children, did }) => {
  const classes = useStyles();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<AttachedFile[]>([]);
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const escFunction = useCallback(event => {
    if (event.keyCode === 27) {
      setOpen(false);
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', escFunction, false);

    return () => {
      document.removeEventListener('keydown', escFunction, false);
    };
  }, []);

  const popoverBody = (
    <div className={classes.main}>
      <div className={classes.heading}>
        <div className={classes.headingText}>
          Files of <b>{did}</b>
        </div>
        <i className={`${classes.headingCloseButton} material-icons`} onClick={() => setOpen(false)}>
          close
        </i>
      </div>
      <div className={classes.content}>
        {loading && (
          <div className={classes.loading}>
            <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
            <span className={classes.iconText}>Loading...</span>
          </div>
        )}
        {files.map(file => (
          <DIDListItem type="file" did={file.did} key={file.did} />
        ))}
      </div>
    </div>
  );

  const loadAttachedFiles = () => {
    setLoading(true);
    setFiles([]);
    actions
      .fetchAttachedFileDIDs(activeInstance.name, did)
      .then(result => setFiles(result))
      .catch(e => console.log(e)) // TODO handle error
      .finally(() => setLoading(false));
  };

  const openPopover = () => {
    setOpen(true);
    loadAttachedFiles();
  };

  return (
    <Popover
      enterExitTransitionDurationMs={0}
      isOpen={open}
      preferPlace="below"
      body={popoverBody}
      onOuterAction={() => setOpen(false)}
    >
      <div onClick={openPopover}>{children}</div>
    </Popover>
  );
};
