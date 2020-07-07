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
    sidebarPanel.activate();
  }
};

export default extension;
