import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Popover from 'react-popover';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../stores/ExtensionStore';
import { TextField } from '../components/TextField';
import { NotebookDIDAttachment } from '../types';

const useStyles = createUseStyles({
  textField: {
    width: '200px'
  },
  instructions: {
    padding: '8px',
    background: '#f5f5f5',
    fontSize: '8pt',
    color: '#808080'
  },
  proceedButton: {
    alignItems: 'center',
    padding: '4px',
    lineHeight: 0,
    cursor: 'pointer'
  },
  proceedIcon: {
    color: '#2196F390',
    fontSize: '16px',
    lineHeight: '24px',
    '&:hover': {
      color: '#2196F3'
    }
  },
  error: {
    color: '#d32f2f'
  }
});

interface AddToNotebookPopoverProps {
  did: string;
  type: 'container' | 'file';
}

type MyProps = React.HTMLAttributes<HTMLDivElement> & AddToNotebookPopoverProps;

export const AddToNotebookPopover: React.FC<MyProps> = ({
  children,
  did,
  type
}) => {
  const classes = useStyles();
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string>();
  const [varName, setVarName] = useState('');
  const activeNotebookPanel = useStoreState(
    ExtensionStore,
    s => s.activeNotebookPanel
  );
  const activeNotebookAttachments = useStoreState(
    ExtensionStore,
    s => s.activeNotebookAttachment
  );

  const existingAttachmentVariableNames = useMemo(
    () =>
      activeNotebookAttachments
        ? activeNotebookAttachments.map(a => a.variableName)
        : [],
    [activeNotebookAttachments]
  );

  const didAttached = useMemo(
    () =>
      activeNotebookAttachments
        ? !!activeNotebookAttachments.find(a => a.did === did)
        : false,
    [activeNotebookAttachments]
  );

  const setActiveNotebookAttachments = (
    attachments: NotebookDIDAttachment[]
  ) => {
    ExtensionStore.update(s => {
      s.activeNotebookAttachment = attachments;
    });
  };

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

  const addAttachment = () => {
    if (!checkVariableNameValid(varName) || checkVariableNameExists(varName)) {
      return;
    }

    setOpen(false);

    const attachment: NotebookDIDAttachment = {
      did,
      type,
      variableName: varName
    };
    const notebookAttachments = activeNotebookAttachments
      ? [...activeNotebookAttachments, attachment]
      : [attachment];

    setActiveNotebookAttachments(notebookAttachments);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      addAttachment();
    }
  };

  const checkVariableNameValid = (variableName: string) => {
    // Empty string
    if (!variableName) {
      return false;
    }

    // Includes non-alphanumeric and non-underscore characters
    if (!variableName.match(/^[a-zA-Z0-9_]*$/)) {
      return false;
    }

    // Begins with number
    if (!isNaN(parseInt(variableName.charAt(0)))) {
      return false;
    }

    return true;
  };

  const checkVariableNameExists = (variableName: string) => {
    return existingAttachmentVariableNames.includes(variableName);
  };

  const handleTextChange = (variableName: string) => {
    setVarName(variableName);
    if (!!variableName && !checkVariableNameValid(variableName)) {
      setError('Invalid variable name');
    } else if (checkVariableNameExists(variableName)) {
      setError('Variable name exists');
    } else {
      setError(undefined);
    }
  };

  const proceedButton = (
    <div className={classes.proceedButton} onClick={addAttachment}>
      <i className={`${classes.proceedIcon} material-icons`}>arrow_forward</i>
    </div>
  );

  const popoverBody = (
    <>
      <TextField
        className={classes.textField}
        outlineColor="#FFFFFF"
        placeholder="Enter a variable name"
        onKeyPress={handleKeyPress}
        after={proceedButton}
        value={varName}
        onChange={e => handleTextChange(e.target.value)}
      />
      <div className={classes.instructions}>
        {!error && <span>Press Enter to proceed, Esc to cancel</span>}
        {!!error && <span className={classes.error}>{error}</span>}
      </div>
    </>
  );

  return (
    <>
      {!!activeNotebookPanel && !didAttached && (
        <Popover
          enterExitTransitionDurationMs={0}
          isOpen={open}
          preferPlace="below"
          body={popoverBody}
          onOuterAction={() => setOpen(false)}
        >
          <div onClick={() => setOpen(!open)}>{children}</div>
        </Popover>
      )}
    </>
  );
};
