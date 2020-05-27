import React from 'react';

import { VDomRenderer } from '@jupyterlab/apputils';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { Session } from '@jupyterlab/services';

import KernelListener from '../helpers/KernelListener';
import { Panel } from '../components/Panel';

export interface ExtensionPanelOptions {
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry;
    widgetId: string;
}

const PANEL_CLASS = 'jp-RucioExtensionPanel';

export class ExtensionPanel extends VDomRenderer {
    app: JupyterFrontEnd;
    weatherData?: any;
    settingRegistry: ISettingRegistry;
    kernelListener: KernelListener;

    constructor(options: ExtensionPanelOptions) {
      super();
      super.addClass(PANEL_CLASS);
      const { app, settingRegistry, widgetId } = options;
  
      super.id = widgetId;
      super.title.closable = true;
      super.title.iconClass += 'jp-icon-rucio';;

      this.app = app;
      this.settingRegistry = settingRegistry;

      const sessionManager = app.serviceManager.sessions;
      this.kernelListener = new KernelListener(sessionManager, {
          connectListeners: [this.onKernelAdded],
          disconnectListeners: [this.onKernelRemoved]
      })
    }

    render() {
      return (<Panel />);
    }

    private onKernelAdded(model: Session.IModel) {
        console.log("Kernel added!", model);
    }

    private onKernelRemoved(kernelId: string) {
        console.log("Kernel removed!", kernelId);
    }
}