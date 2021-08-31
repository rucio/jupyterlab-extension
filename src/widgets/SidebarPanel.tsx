/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
 */

import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';
import { VDomRenderer } from '@jupyterlab/apputils';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { useStoreState } from 'pullstate';
import { InstanceConfig } from '../types';
import { Header } from '../components/Header';
import { UIStore } from '../stores/UIStore';
import { rucioIcon } from '../icons/RucioIcon';
import { MenuBar } from '../components/MenuBar';
import { ExploreTab } from '../components/@Explore/ExploreTab';
import { NotebookTab } from '../components/@Notebook/NotebookTab';
import { SettingsTab } from '../components/@Settings/SettingsTab';
import { UploadsTab } from '../components/@Uploads/UploadsTab';
import { JupyterLabAppContext } from '../const';

const useStyles = createUseStyles({
  panel: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  },
  section: {
    flex: 1
  },
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  iconText: {
    verticalAlign: 'middle',
    paddingLeft: '4px'
  },
  container: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'auto'
  },
  menuBar: {
    marginTop: '16px'
  },
  content: {
    flex: 1,
    overflow: 'auto',
    '& > div': {
      height: '100%'
    }
  },
  instanceOption: {
    lineHeight: 0
  },
  infoIcon: {
    fontSize: '15px'
  },
  hidden: {
    display: 'none'
  }
});

const Panel: React.FC = () => {
  const classes = useStyles();
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const [activeMenu, setActiveMenu] = useState(activeInstance ? 1 : 3);

  const menus = [
    { title: 'Explore', value: 1, right: false, disabled: !activeInstance },
    { title: 'Notebook', value: 2, right: false, disabled: !activeInstance },
    {
      title: (
        <div className={classes.instanceOption}>
          <i className={`${classes.infoIcon} material-icons`}>settings</i>
        </div>
      ),
      value: 3,
      right: true
    },
    {
      title: (
        <div className={classes.instanceOption}>
          <i className={`${classes.infoIcon} material-icons`}>upload</i>
        </div>
      ),
      value: 4,
      right: true
    }
  ];

  return (
    <div className={classes.panel}>
      <Header />
      <div className={classes.container}>
        <div className={classes.menuBar}>
          <MenuBar menus={menus} value={activeMenu} onChange={setActiveMenu} />
        </div>
        <div className={classes.content}>
          <div className={activeMenu !== 1 ? classes.hidden : ''}>{activeInstance && <ExploreTab />}</div>
          <div className={activeMenu !== 2 ? classes.hidden : ''}>{activeInstance && <NotebookTab />}</div>
          <div className={activeMenu !== 3 ? classes.hidden : ''}>
            <SettingsTab />
          </div>
          <div className={activeMenu !== 4 ? classes.hidden : ''}>
            <UploadsTab visible={activeMenu === 4} />
          </div>
        </div>
      </div>
    </div>
  );
};

const ErrorPanel: React.FC<{ error: string }> = ({ error }) => {
  const classes = useStyles();

  return <div className={classes.content}>{error}</div>;
};

export interface SidebarPanelOptions {
  app: JupyterFrontEnd;
  instanceConfig: InstanceConfig;
}

const PANEL_CLASS = 'jp-RucioExtensionPanel';

export class SidebarPanel extends VDomRenderer {
  error?: string;
  instanceConfig?: InstanceConfig;
  app: JupyterFrontEnd;

  constructor(options: SidebarPanelOptions, error?: string) {
    super();
    super.addClass(PANEL_CLASS);
    super.title.closable = true;
    super.title.icon = rucioIcon;

    const { app, instanceConfig } = options;
    this.app = app;

    if (error) {
      this.error = error ?? 'Failed to activate extension. Make sure that the extension is configured and installed properly.';
      return;
    }

    this.instanceConfig = instanceConfig;
    this.populateUIStore(instanceConfig);
  }

  private populateUIStore(instanceConfig: InstanceConfig) {
    const { activeInstance, authType, instances } = instanceConfig;
    const objActiveInstance = instances.find(i => i.name === activeInstance);
    UIStore.update(s => {
      s.activeInstance = objActiveInstance;
      s.activeAuthType = authType;
      s.instances = instances;
    });
  }

  render(): React.ReactElement {
    if (this.error) {
      return <ErrorPanel error={this.error} />;
    }

    if (!this.instanceConfig) {
      return <ErrorPanel error="Extension is not configured properly." />;
    }

    return (
      <JupyterLabAppContext.Provider value={this.app}>
        <Panel />
      </JupyterLabAppContext.Provider>
    );
  }
}
