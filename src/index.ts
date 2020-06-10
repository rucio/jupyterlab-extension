import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell
} from '@jupyterlab/application';

import { INotebookTracker } from '@jupyterlab/notebook';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ICommandPalette } from '@jupyterlab/apputils';

import { EXTENSION_ID } from './const';
import { ExtensionPanel } from './PanelExtension';
import EventBus from './utils/EventBus';

/**
 * Initialization data for the rucio-jupyterlab extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: EXTENSION_ID,
  autoStart: true,
  requires: [ICommandPalette, ILabShell, ISettingRegistry, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    labShell: ILabShell,
    settingRegistry: ISettingRegistry,
    notebooks: INotebookTracker
  ) => {
    console.log('JupyterLab extension rucio-jupyterlab is activated!');

    const panel = new ExtensionPanel({
      app,
      settingRegistry,
      widgetId: `${EXTENSION_ID}:panel`
    });

    labShell.add(panel, 'left', { rank: 900 });
    labShell.activateById(panel.id);

    labShell.currentChanged.connect(() => {
      const widget = labShell.currentWidget;
      const nbWidget = notebooks.currentWidget;
      if (widget === nbWidget) {
        EventBus.activeNotebook(nbWidget);
      } else {
        EventBus.activeNotebook(undefined);
      }
    });
  }
};

export default extension;
