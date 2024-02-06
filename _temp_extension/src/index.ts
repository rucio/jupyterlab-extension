import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { requestAPI } from './handler';

/**
 * Initialization data for the rucio-jupyterlab extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'rucio-jupyterlab:plugin',
  description: 'JupyterLab extension for integrating Rucio',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension rucio-jupyterlab is activated!');

    requestAPI<any>('get-example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The rucio_jupyterlab server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
