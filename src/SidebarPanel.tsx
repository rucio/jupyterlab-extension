import React, { useEffect, useState } from 'react';
import { createUseStyles } from 'react-jss';

import { VDomRenderer } from '@jupyterlab/apputils';
import { JupyterFrontEnd, ILabShell } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { INotebookTracker } from '@jupyterlab/notebook';
import { NotebookListener } from './listeners/NotebookListener';
import { InstanceConfig } from './types';
import { Header } from './components/Header';
import { MainPanel } from './pages/MainPanel';
import { Spinning } from './components/Spinning';
import { UIStore } from './stores/UIStore';

const useStyles = createUseStyles({
  panel: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  },
  section: {
    flex: 1
  },
  loading: {
    padding: '8px 16px 8px 16px'
  },
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  iconText: {
    verticalAlign: 'middle',
    paddingLeft: '4px'
  }
});

interface PanelProps {
  instanceConfig: InstanceConfig;
}

const Panel: React.FC<PanelProps> = ({ instanceConfig }) => {
  const classes = useStyles();
  const { activeInstance, authType, instances } = instanceConfig;
  const [configLoaded, setConfigLoaded] = useState(false);

  useEffect(() => {
    const objActiveInstance = instances.find(i => i.name === activeInstance);
    UIStore.update(s => {
      s.activeInstance = objActiveInstance;
      s.activeAuthType = authType;
      s.instances = instances;
    });
    setConfigLoaded(true);
  }, [instanceConfig]);

  return (
    <div className={classes.panel}>
      <Header />
      {!!configLoaded && <MainPanel />}
      {!configLoaded && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
          <span className={classes.iconText}>Loading...</span>
        </div>
      )}
    </div>
  );
};

export interface SidebarPanelOptions {
  app: JupyterFrontEnd;
  settingRegistry: ISettingRegistry;
  labShell: ILabShell;
  notebookTracker: INotebookTracker;
  widgetId: string;
  instanceConfig: InstanceConfig;
}

const PANEL_CLASS = 'jp-RucioExtensionPanel';

export class SidebarPanel extends VDomRenderer {
  app: JupyterFrontEnd;
  settingRegistry: ISettingRegistry;
  notebookListener: NotebookListener;
  instanceConfig: InstanceConfig;

  constructor(options: SidebarPanelOptions) {
    super();
    super.addClass(PANEL_CLASS);
    const { app, settingRegistry, labShell, notebookTracker, widgetId, instanceConfig } = options;

    super.id = widgetId;
    super.title.closable = true;
    super.title.iconClass += 'jp-icon-rucio';

    this.app = app;
    this.settingRegistry = settingRegistry;
    this.instanceConfig = instanceConfig;

    this.notebookListener = new NotebookListener({
      labShell,
      notebookTracker,
      sessionManager: app.serviceManager.sessions
    });

    this.notebookListener.setup();
  }

  render(): React.ReactElement {
    return <Panel instanceConfig={this.instanceConfig} />;
  }
}
