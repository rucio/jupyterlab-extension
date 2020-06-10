import React from 'react';

import { VDomRenderer } from '@jupyterlab/apputils';
import { JupyterFrontEnd, ILabShell } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { Panel } from './Panel';
import { ExtensionStore } from './stores/ExtensionStore';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

export interface ExtensionPanelOptions {
  app: JupyterFrontEnd;
  settingRegistry: ISettingRegistry;
  labShell: ILabShell;
  notebooks: INotebookTracker;
  widgetId: string;
}

const PANEL_CLASS = 'jp-RucioExtensionPanel';

export class ExtensionPanel extends VDomRenderer {
  app: JupyterFrontEnd;
  weatherData?: any;
  settingRegistry: ISettingRegistry;

  constructor(options: ExtensionPanelOptions) {
    super();
    super.addClass(PANEL_CLASS);
    const { app, settingRegistry, labShell, notebooks, widgetId } = options;

    super.id = widgetId;
    super.title.closable = true;
    super.title.iconClass += 'jp-icon-rucio';

    this.app = app;
    this.settingRegistry = settingRegistry;

    const setActiveNotebook = (activeNotebook?: NotebookPanel) => {
      console.log('Set active notebook', activeNotebook);
      ExtensionStore.update(s => {
        s.activeNotebookPanel = activeNotebook;
      });
    };

    labShell.currentChanged.connect(() => {
      const widget = labShell.currentWidget;
      const nbWidget = notebooks.currentWidget;
      if (widget === nbWidget) {
        nbWidget.revealed.then(() => {
          setActiveNotebook(nbWidget);
        });
      } else {
        setActiveNotebook(undefined);
      }
    });
  }

  render(): React.ReactElement {
    return <Panel />;
  }
}
