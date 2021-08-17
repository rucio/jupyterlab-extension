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

import { JupyterFrontEnd, JupyterFrontEndPlugin, ILabShell } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import { EXTENSION_ID } from './const';
import { SidebarPanel } from './widgets/SidebarPanel';
import { actions } from './utils/Actions';
import { NotebookListener } from './utils/NotebookListener';
import { ActiveNotebookListener } from './utils/ActiveNotebookListener';
import { NotebookPollingListener } from './utils/NotebookPollingListener';
import { InstanceConfig } from './types';

/**
 * Initialization data for the rucio-jupyterlab extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: EXTENSION_ID,
  autoStart: true,
  requires: [ILabShell, INotebookTracker],
  activate: async (app: JupyterFrontEnd, labShell: ILabShell, notebookTracker: INotebookTracker) => {
    try {
      const instanceConfig = await actions.fetchInstancesConfig();
      activateSidebarPanel(app, labShell, instanceConfig);
      activateNotebookListener(app, labShell, notebookTracker);
    } catch (e) {
      console.log(e);
    }
  }
};

function activateSidebarPanel(app: JupyterFrontEnd, labShell: ILabShell, instanceConfig: InstanceConfig) {
  const sidebarPanel = new SidebarPanel({ app, instanceConfig });
  sidebarPanel.id = EXTENSION_ID + ':panel';
  labShell.add(sidebarPanel, 'left', { rank: 900 });
  labShell.activateById(sidebarPanel.id);
}

function activateNotebookListener(app: JupyterFrontEnd, labShell: ILabShell, notebookTracker: INotebookTracker) {
  const notebookListener = new NotebookListener({
    labShell,
    notebookTracker,
    sessionManager: app.serviceManager.sessions
  });

  new ActiveNotebookListener({
    labShell,
    notebookTracker,
    sessionManager: app.serviceManager.sessions,
    notebookListener: notebookListener
  });

  new NotebookPollingListener(notebookListener);
}

export default extension;
