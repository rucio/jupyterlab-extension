import { JupyterFrontEnd, JupyterFrontEndPlugin, ILabShell } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { EXTENSION_ID } from './const';
import { SidebarPanel } from './SidebarPanel';
import { actions } from './utils/Actions';

/**
 * Initialization data for the rucio-jupyterlab extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: EXTENSION_ID,
  autoStart: true,
  requires: [ILabShell, ISettingRegistry, INotebookTracker],
  activate: async (
    app: JupyterFrontEnd,
    labShell: ILabShell,
    settingRegistry: ISettingRegistry,
    notebookTracker: INotebookTracker
  ) => {
    const instanceConfig = await actions.fetchInstancesConfig();
    const options = {
      app,
      settingRegistry,
      labShell,
      notebookTracker,
      widgetId: `${EXTENSION_ID}:panel`,
      instanceConfig
    };

    const sidebarPanel = new SidebarPanel(options);
    labShell.add(sidebarPanel, 'left', { rank: 900 });
    labShell.activateById(sidebarPanel.id);
  }
};

export default extension;
