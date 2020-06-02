import React, { useState, useEffect } from 'react';
import { useStoreState } from 'pullstate';
import { createUseStyles } from 'react-jss';
import { ExtensionStore } from './stores/ExtensionStore';
import { Header } from './components/Header';
import { MainPanel } from './pages/MainPanel';
import { SelectInstance } from './pages/SelectInstance';
import { requestAPI } from './utils/ApiRequest';
import { Instance } from './types';

const useStyles = createUseStyles({
  '@keyframes rotation': {
    from: {
      transform: 'rotate(0deg)'
    },
    to: {
      transform: 'rotate(359deg)'
    }
  },
  rotate: {
    animation: '$rotation 1s infinite linear',
    animationName: '$rotation'
  },
  panel: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  },
  section: {
    flex: 1
  },
  loading: {
    padding: '8px 16px 8px 16px',
    '& span': {
      verticalAlign: 'middle',
      paddingLeft: '4px'
    }
  },
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  }
});

export const Panel: React.FunctionComponent = () => {
  const classes = useStyles();
  const activeInstance = useStoreState(ExtensionStore, s => s.activeInstance);

  const [instances, setInstances] = useState<Instance[]>(undefined);

  useEffect(() => {
    loadInstances();
  }, []);

  const loadInstances = () => {
    requestAPI<{ activeInstance?: string; instances: Instance[] }>('instances')
      .then(({ activeInstance, instances }) =>
        instancesLoaded(activeInstance, instances)
      )
      .catch(e => console.log(e));
  };

  const instancesLoaded = (activeInstance: string, instances: Instance[]) => {
    const objActiveInstance = instances.find(i => i.name === activeInstance);
    if (objActiveInstance) {
      console.log('Active instance: ', activeInstance);

      ExtensionStore.update(s => {
        s.activeInstance = objActiveInstance;
      });
    }

    setInstances(instances);
  };

  const setActiveInstance = (value?: string) => {
    ExtensionStore.update(s => {
      const instance = instances.find(i => i.name === value);
      s.activeInstance = instance;
    });

    const init = {
      method: 'PUT',
      body: JSON.stringify({
        instance: value
      })
    };

    requestAPI('instances', init).catch(e => console.log(e));
  };

  return (
    <div className={classes.panel}>
      <Header />
      {!!activeInstance && <MainPanel />}
      {!instances && (
        <div className={classes.loading}>
          <i className={`${classes.icon} ${classes.rotate} material-icons`}>
            hourglass_top
          </i>
          <span>Loading...</span>
        </div>
      )}
      {!activeInstance && !!instances && (
        <SelectInstance
          instances={instances}
          onSelectInstance={setActiveInstance}
        />
      )}
    </div>
  );
};
