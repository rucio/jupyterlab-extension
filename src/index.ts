import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell
} from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ICommandPalette } from '@jupyterlab/apputils';

import { EXTENSION_ID } from './const';
import { ExtensionPanel } from './PanelExtension';

/**
 * Initialization data for the rucio-jupyterlab extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: EXTENSION_ID,
  autoStart: true,
  requires: [ICommandPalette, ILabShell, ISettingRegistry],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    labShell: ILabShell,
    settingRegistry: ISettingRegistry
  ) => {
    console.log('JupyterLab extension rucio-jupyterlab is activated!');

    const panel = new ExtensionPanel({
      app,
      settingRegistry,
      widgetId: `${EXTENSION_ID}:panel`
    });

    labShell.add(panel, 'left', { rank: 900 });
    labShell.activateById(panel.id);
  }
};

export default extension;
