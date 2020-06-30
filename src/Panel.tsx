import React, { useState, useEffect } from 'react';
import { createUseStyles } from 'react-jss';
import { UIStore } from './stores/UIStore';
import { Header } from './components/Header';
import { MainPanel } from './pages/MainPanel';
import { Instance, RucioAuthType } from './types';
import { Spinning } from './components/Spinning';
import { WithRequestAPIProps, withRequestAPI } from './utils/Actions';

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

const _Panel: React.FunctionComponent = props => {
  const classes = useStyles();
  const { actions } = props as WithRequestAPIProps;

  const [instances, setInstances] = useState<Instance[]>(undefined);

  useEffect(() => {
    loadInstances();
  }, []);

  const loadInstances = () => {
    actions
      .fetchInstancesConfig()
      .then(({ activeInstance, instances, authType }) => instancesLoaded(activeInstance, authType, instances))
      .catch(e => console.log(e));
  };

  const instancesLoaded = (activeInstance: string, authType: RucioAuthType, instances: Instance[]) => {
    const objActiveInstance = instances.find(i => i.name === activeInstance);
    UIStore.update(s => {
      s.activeInstance = objActiveInstance;
      s.activeAuthType = authType;
      s.instances = instances;
    });

    setInstances(instances);
  };

  return (
    <div className={classes.panel}>
      <Header />
      {!!instances && <MainPanel />}
      {!instances && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
          <span className={classes.iconText}>Loading...</span>
        </div>
      )}
    </div>
  );
};

export const Panel = withRequestAPI(_Panel);
