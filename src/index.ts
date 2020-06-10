import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell
} from '@jupyterlab/application';

import { INotebookTracker } from '@jupyterlab/notebook';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { EXTENSION_ID } from './const';
import { ExtensionPanel } from './PanelExtension';

/**
 * Initialization data for the rucio-jupyterlab extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: EXTENSION_ID,
  autoStart: true,
  requires: [ILabShell, ISettingRegistry, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    labShell: ILabShell,
    settingRegistry: ISettingRegistry,
    notebooks: INotebookTracker
  ) => {
    console.log('JupyterLab extension rucio-jupyterlab is activated!');

    const panel = new ExtensionPanel({
      app,
      settingRegistry,
      labShell,
      notebooks,
      widgetId: `${EXTENSION_ID}:panel`
    });

    labShell.add(panel, 'left', { rank: 900 });
    labShell.activateById(panel.id);
  }
};

export default extension;
