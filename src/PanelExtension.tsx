import React from 'react';

import { VDomRenderer } from '@jupyterlab/apputils';
import { JupyterFrontEnd, ILabShell } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { Panel } from './Panel';
import { ExtensionStore, ExtensionState } from './stores/ExtensionStore';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { ReadonlyPartialJSONArray } from '@lumino/coreutils';
import { NotebookDIDAttachment } from './types';
import { METADATA_KEY } from './const';

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
      ExtensionStore.update(s => {
        s.activeNotebookPanel = activeNotebook;
      });
    };

    const setActiveNotebookAttachments = (
      attachments: NotebookDIDAttachment[]
    ) => {
      ExtensionStore.update(s => {
        s.activeNotebookAttachment = attachments;
      });
    };

    const onNotebookAttachmentChanged = (
      attachments: NotebookDIDAttachment[],
      state: ExtensionState
    ) => {
      if (attachments) {
        const { metadata } = state.activeNotebookPanel.model;
        const current = metadata.get(METADATA_KEY) as ReadonlyArray<any>;
        const rucioDidAttachments = attachments as ReadonlyArray<any>;

        if (current !== rucioDidAttachments) {
          metadata.set(
            METADATA_KEY,
            rucioDidAttachments as ReadonlyPartialJSONArray
          );
        }
      }
    };

    ExtensionStore.subscribe(
      s => s.activeNotebookAttachment,
      onNotebookAttachmentChanged
    );

    const onActiveTabChanged = () => {
      const widget = labShell.currentWidget;
      const nbWidget = notebooks.currentWidget;
      if (!!widget && widget === nbWidget) {
        nbWidget.revealed.then(() => {
          setActiveNotebook(nbWidget);
          const rucioDidAttachments = nbWidget.model.metadata.get(METADATA_KEY);
          if (rucioDidAttachments) {
            const attachedDIDs = rucioDidAttachments as ReadonlyArray<any>;
            setActiveNotebookAttachments(
              attachedDIDs as NotebookDIDAttachment[]
            );
          } else {
            setActiveNotebookAttachments(undefined);
          }
        });
      } else {
        setActiveNotebook(undefined);
        setActiveNotebookAttachments(undefined);
      }
    };

    labShell.currentChanged.connect(onActiveTabChanged);
  }

  render(): React.ReactElement {
    return <Panel />;
  }
}
