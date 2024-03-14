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

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
// import { fileUploadIcon } from '@jupyterlab/ui-components';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
// import { toArray } from '@lumino/algorithm';
// import { CommandIDs } from './const';
import { EXTENSION_ID } from './const';
import { SidebarPanel } from './widgets/SidebarPanel';
import { actions } from './utils/Actions';
import { NotebookListener } from './utils/NotebookListener';
import { ActiveNotebookListener } from './utils/ActiveNotebookListener';
import { NotebookPollingListener } from './utils/NotebookPollingListener';
import { IInstanceConfig } from './types';
// import uploadFile from './commands/uploadFile';
import { SessionManager } from '@jupyterlab/services';

/**
 * Initialization data for the rucio-jupyterlab extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: EXTENSION_ID,
  autoStart: true,
  requires: [ILabShell, INotebookTracker, IFileBrowserFactory],
  activate: async (
    app: JupyterFrontEnd,
    labShell: ILabShell,
    notebookTracker: INotebookTracker,
    fileBrowserFactory: IFileBrowserFactory
  ) => {
    try {
      const instanceConfig = await actions.fetchInstancesConfig();
      activateSidebarPanel(app, labShell, instanceConfig);
      activateNotebookListener(app, labShell, notebookTracker);
      //       activateRucioUploadWidget(app, fileBrowserFactory);
    } catch (e) {
      console.log(e);
    }
  }
};

function activateSidebarPanel(
  app: JupyterFrontEnd,
  labShell: ILabShell,
  instanceConfig: IInstanceConfig
) {
  const sidebarPanel = new SidebarPanel({ app, instanceConfig });
  sidebarPanel.id = EXTENSION_ID + ':panel';
  labShell.add(sidebarPanel, 'left', { rank: 900 });
  labShell.activateById(sidebarPanel.id);
}

function activateNotebookListener(
  app: JupyterFrontEnd,
  labShell: ILabShell,
  notebookTracker: INotebookTracker
) {
  const notebookListener = new NotebookListener({
    labShell,
    notebookTracker,
    sessionManager: app.serviceManager.sessions as SessionManager
  });

  new ActiveNotebookListener({
    labShell,
    notebookTracker,
    sessionManager: app.serviceManager.sessions as SessionManager,
    notebookListener: notebookListener
  });

  new NotebookPollingListener(notebookListener);
}

/*function activateRucioUploadWidget(
  app: JupyterFrontEnd,
  fileBrowserFactory: IFileBrowserFactory
) {
  app.commands.addCommand(CommandIDs.UploadFile, {
    icon: fileUploadIcon,
    label: 'Upload File(s) to Rucio',
    execute: async () => {
      const widget = fileBrowserFactory.tracker.currentWidget;

      if (widget) {
        const selection = toArray(widget.selectedItems()).filter(
          s => s.type !== 'directory'
        );
        if (selection.length === 0) {
          return;
        }
        uploadFile(selection);
      }
    }
  });

  app.contextMenu.addItem({
    command: CommandIDs.UploadFile,
    selector: '.jp-DirListing-item[data-isdir="false"]',
    rank: 10
  });
}*/

export default extension;
