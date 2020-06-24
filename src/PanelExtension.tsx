import React from 'react';

import { VDomRenderer } from '@jupyterlab/apputils';
import { JupyterFrontEnd, ILabShell } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { Panel } from './Panel';
import { INotebookTracker } from '@jupyterlab/notebook';
import { NotebookListener } from './listeners/NotebookListener';

export interface ExtensionPanelOptions {
  app: JupyterFrontEnd;
  settingRegistry: ISettingRegistry;
  labShell: ILabShell;
  notebookTracker: INotebookTracker;
  widgetId: string;
}

const PANEL_CLASS = 'jp-RucioExtensionPanel';

export class ExtensionPanel extends VDomRenderer {
  app: JupyterFrontEnd;
  weatherData?: any;
  settingRegistry: ISettingRegistry;
  notebookListener: NotebookListener;

  constructor(options: ExtensionPanelOptions) {
    super();
    super.addClass(PANEL_CLASS);
    const { app, settingRegistry, labShell, notebookTracker, widgetId } = options;

    super.id = widgetId;
    super.title.closable = true;
    super.title.iconClass += 'jp-icon-rucio';

    this.app = app;
    this.settingRegistry = settingRegistry;

    this.notebookListener = new NotebookListener({
      labShell,
      notebookTracker,
      sessionManager: app.serviceManager.sessions
    });
    this.notebookListener.setup();
  }

  render(): React.ReactElement {
    return <Panel />;
  }
}
