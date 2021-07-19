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

import React, { useEffect, useState } from 'react';
import { createUseStyles } from 'react-jss';

import { VDomRenderer } from '@jupyterlab/apputils';
import { JupyterFrontEnd, ILabShell } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import { NotebookListener } from './utils/NotebookListener';
import { ActiveNotebookListener } from './utils/ActiveNotebookListener';
import { InstanceConfig } from './types';
import { Header } from './components/Header';
import { MainPanel } from './pages/MainPanel';
import { Spinning } from './components/Spinning';
import { UIStore } from './stores/UIStore';
import { NotebookPollingListener } from './utils/NotebookPollingListener';
import { rucioIcon } from './icons/RucioIcon';

const useStyles = createUseStyles({
  panel: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  },
  section: {
    flex: 1
  },
  content: {
    padding: '16px'
  },
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  iconText: {
    verticalAlign: 'middle',
    paddingLeft: '4px'
  }
});

interface PanelProps {
  instanceConfig: InstanceConfig;
}

const Panel: React.FC<PanelProps> = ({ instanceConfig }) => {
  const classes = useStyles();
  const { activeInstance, authType, instances } = instanceConfig;
  const [configLoaded, setConfigLoaded] = useState(false);

  useEffect(() => {
    const objActiveInstance = instances.find(i => i.name === activeInstance);
    UIStore.update(s => {
      s.activeInstance = objActiveInstance;
      s.activeAuthType = authType;
      s.instances = instances;
    });
    setConfigLoaded(true);
  }, [instanceConfig]);

  return (
    <div className={classes.panel}>
      <Header />
      {!!configLoaded && <MainPanel />}
      {!configLoaded && (
        <div className={classes.content}>
          <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
          <span className={classes.iconText}>Loading...</span>
        </div>
      )}
    </div>
  );
};

const ErrorPanel: React.FC<{ error: string }> = ({ error }) => {
  const classes = useStyles();

  return <div className={classes.content}>{error}</div>;
};

export interface SidebarPanelOptions {
  app: JupyterFrontEnd;
  labShell: ILabShell;
  notebookTracker: INotebookTracker;
  instanceConfig: InstanceConfig;
}

const PANEL_CLASS = 'jp-RucioExtensionPanel';

export class SidebarPanel extends VDomRenderer {
  error?: string;
  app?: JupyterFrontEnd;
  notebookListener?: NotebookListener;
  activeNotebookListener?: ActiveNotebookListener;
  notebookPollingListener?: NotebookPollingListener;
  instanceConfig?: InstanceConfig;

  constructor(options?: SidebarPanelOptions, error?: string) {
    super();
    super.addClass(PANEL_CLASS);
    super.title.closable = true;
    super.title.icon = rucioIcon;

    if (!options || error) {
      this.error = error || 'Failed to activate extension. Make sure that the extension is configured and installed properly.';
      return;
    }

    const { app, labShell, notebookTracker, instanceConfig } = options;

    this.app = app;
    this.instanceConfig = instanceConfig;

    this.notebookListener = new NotebookListener({
      labShell,
      notebookTracker,
      sessionManager: app.serviceManager.sessions
    });

    this.activeNotebookListener = new ActiveNotebookListener({
      labShell,
      notebookTracker,
      sessionManager: app.serviceManager.sessions,
      notebookListener: this.notebookListener
    });

    this.notebookPollingListener = new NotebookPollingListener(this.notebookListener);
  }

  render(): React.ReactElement {
    if (this.error) {
      return <ErrorPanel error={this.error} />;
    }

    if (!this.instanceConfig) {
      return <ErrorPanel error="Extension is not configured properly." />;
    }

    return <Panel instanceConfig={this.instanceConfig} />;
  }
}
