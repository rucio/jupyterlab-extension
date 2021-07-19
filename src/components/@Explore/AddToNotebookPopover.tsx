/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
 */

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import Popover from 'react-popover';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../../stores/ExtensionStore';
import { TextField } from '../TextField';
import { NotebookDIDAttachment } from '../../types';
import { checkVariableNameValid } from '../../utils/Helpers';

const useStyles = createUseStyles({
  main: {
    background: 'var(--jp-layout-color1)',
    color: 'var(--jp-ui-font-color1)'
  },
  textField: {
    width: '200px',
    background: 'var(--jp-layout-color1)',
    color: 'var(--jp-ui-font-color1)'
  },
  instructions: {
    padding: '8px',
    fontSize: '8pt',
    background: 'var(--jp-layout-color2)',
    color: 'var(--jp-ui-font-color2)'
  },
  proceedButton: {
    alignItems: 'center',
    padding: '4px',
    lineHeight: 0,
    cursor: 'pointer'
  },
  proceedIcon: {
    color: 'var(--jp-rucio-primary-blue-color)',
    opacity: 0.5,
    fontSize: '16px',
    lineHeight: '24px',
    '&:hover': {
      color: 'var(--jp-rucio-primary-blue-color)',
      opacity: 1
    }
  },
  error: {
    color: 'var(--jp-error-color2)'
  }
});

interface AddToNotebookPopoverProps {
  did: string;
  type: 'collection' | 'file';
}

type MyProps = React.HTMLAttributes<HTMLDivElement> & AddToNotebookPopoverProps;

export const AddToNotebookPopover: React.FC<MyProps> = ({ children, did, type }) => {
  const classes = useStyles();
  const textFieldRef = useRef<HTMLInputElement>(null);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string>();
  const [varName, setVarName] = useState('');
  const activeNotebookPanel = useStoreState(ExtensionStore, s => s.activeNotebookPanel);
  const activeNotebookAttachments = useStoreState(ExtensionStore, s => s.activeNotebookAttachment);

  const existingAttachmentVariableNames = useMemo(
    () => (activeNotebookAttachments ? activeNotebookAttachments.map(a => a.variableName) : []),
    [activeNotebookAttachments]
  );

  const didAttached = useMemo(
    () => (activeNotebookAttachments ? !!activeNotebookAttachments.find(a => a.did === did) : false),
    [activeNotebookAttachments]
  );

  const setActiveNotebookAttachments = (attachments: NotebookDIDAttachment[]) => {
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
    const notebookAttachments = activeNotebookAttachments ? [...activeNotebookAttachments, attachment] : [attachment];

    setActiveNotebookAttachments(notebookAttachments);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      addAttachment();
    }
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
    <div className={classes.main}>
      <TextField
        ref={textFieldRef}
        className={classes.textField}
        outlineColor="var(--jp-layout-color1)"
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
    </div>
  );

  const openPopover = () => {
    setOpen(true);
    setVarName('');
    setError(undefined);
    setTimeout(() => {
      textFieldRef.current?.focus();
    }, 10);
  };

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
          <div onClick={openPopover}>{children}</div>
        </Popover>
      )}
    </>
  );
};
