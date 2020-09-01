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
import { SidebarPanel } from './SidebarPanel';
import { actions } from './utils/Actions';

/**
 * Initialization data for the rucio-jupyterlab extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: EXTENSION_ID,
  autoStart: true,
  requires: [ILabShell, INotebookTracker],
  activate: async (app: JupyterFrontEnd, labShell: ILabShell, notebookTracker: INotebookTracker) => {
    let options;

    try {
      const instanceConfig = await actions.fetchInstancesConfig();
      options = {
        app,
        labShell,
        notebookTracker,
        instanceConfig
      };
    } catch (e) {
      console.log(e);
    }

    const sidebarPanel = new SidebarPanel(options);
    sidebarPanel.id = EXTENSION_ID + ':panel';
    labShell.add(sidebarPanel, 'left', { rank: 900 });
    labShell.activateById(sidebarPanel.id);
  }
};

export default extension;
