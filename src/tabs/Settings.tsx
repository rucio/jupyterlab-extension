import React, { useMemo, useState, useEffect } from 'react';
import { createUseStyles } from 'react-jss';
import Select from 'react-select';
import { useStoreState } from 'pullstate';
import { UIStore, resetRucioCaches } from '../stores/UIStore';
import { Button } from '../components/Button';
import { withRequestAPI, WithRequestAPIProps } from '../utils/Actions';
import { authTypeOptions } from '../const';
import { UserPassAuth } from '../components/@Settings/UserPassAuth';
import { X509Auth } from '../components/@Settings/X509Auth';
import { RucioAuthType, RucioAuthCredentials, RucioUserpassAuth, RucioX509Auth } from '../types';
import { HorizontalHeading } from '../components/HorizontalHeading';

const useStyles = createUseStyles({
  content: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  },
  scrollable: {
    flex: 1,
    overflow: 'auto'
  },
  container: {
    padding: '16px'
  },
  buttonContainer: {
    extend: 'container',
    borderTop: '1px solid #e0e0e0'
  },
  label: {},
  instanceName: {
    fontSize: '16pt'
  },
  formControl: {
    marginTop: '8px'
  },
  formItem: {
    marginBottom: '16px'
  }
});

const _Settings: React.FunctionComponent = props => {
  const { actions } = props as WithRequestAPIProps;

  const classes = useStyles();
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);
  const instances = useStoreState(UIStore, s => s.instances) || [];

  const instanceDefaultValue = activeInstance ? { label: activeInstance.displayName, value: activeInstance.name } : null;

  const [selectedInstance, setSelectedInstance] = useState<string>(instanceDefaultValue?.value);
  const [selectedAuthType, setSelectedAuthType] = useState<RucioAuthType>();
  const [rucioAuthCredentials, setRucioAuthCredentials] = useState<RucioAuthCredentials>();

  const instanceOptions = useMemo(() => instances?.map(i => ({ label: i.displayName, value: i.name })), [instances]);

  const setActiveInstance = (value?: string) => {
    resetRucioCaches();

    UIStore.update(s => {
      const instance = instances.find(i => i.name === value);
      s.activeInstance = instance;
    });

    actions.postActiveInstance(value).catch(e => console.log(e));
  };

  const setRucioAuthConfig = (namespace: string, authType: RucioAuthType, rucioAuthCredentials: RucioAuthCredentials) => {
    actions.putAuthConfig(namespace, authType, rucioAuthCredentials);
  };

  const saveSettings = () => {
    if (selectedInstance) {
      setActiveInstance(selectedInstance);
    }

    if (!!setSelectedAuthType && !!rucioAuthCredentials) {
      setRucioAuthConfig(selectedInstance, selectedAuthType, rucioAuthCredentials);
    }
  };

  const selectStyles = {
    control: (provided: any, state: any) => ({
      ...provided,
      borderRadius: 0
    })
  };

  const reloadAuthConfig = () => {
    if (!selectedInstance) {
      return;
    }

    setRucioAuthCredentials(undefined);
    actions
      .getAuthConfig<any>(selectedInstance, selectedAuthType)
      .then(c => setRucioAuthCredentials(c))
      .catch(() => {
        switch (selectedAuthType) {
          case 'userpass':
            setRucioAuthCredentials({ username: '', password: '', account: '' });
            break;
          case 'x509':
            setRucioAuthCredentials({ username: '', password: '', account: '' });
            break;
        }
      });
  };

  useEffect(reloadAuthConfig, [selectedInstance, selectedAuthType]);

  return (
    <div className={classes.content}>
      <div className={classes.scrollable}>
        <div className={classes.container}>
          <div className={classes.formItem}>
            <div className={classes.label}>Active Instance</div>
            <Select
              className={classes.formControl}
              options={instanceOptions}
              styles={selectStyles}
              defaultValue={instanceDefaultValue}
              onChange={(value: any) => {
                setSelectedInstance(value.value);
              }}
            />
          </div>
          <div className={classes.formItem}>
            <div className={classes.label}>Rucio Authentication</div>
            <Select
              className={classes.formControl}
              options={authTypeOptions}
              styles={selectStyles}
              onChange={(value: any) => {
                setSelectedAuthType(value.value);
              }}
            />
          </div>
        </div>
        <div>
          {selectedAuthType === 'userpass' && !!selectedInstance && (
            <>
              <HorizontalHeading title="Username &amp; Password" />
              {!!rucioAuthCredentials && (
                <UserPassAuth params={rucioAuthCredentials as RucioUserpassAuth} onChange={v => setRucioAuthCredentials(v)} />
              )}
              {!rucioAuthCredentials && !selectedInstance && <div className={classes.container}>Loading...</div>}
            </>
          )}
          {selectedAuthType === 'x509' && !!selectedInstance && (
            <>
              <HorizontalHeading title="X.509 User Certificate" />
              {!!rucioAuthCredentials && (
                <X509Auth params={rucioAuthCredentials as RucioX509Auth} onChange={v => setRucioAuthCredentials(v)} />
              )}
              {!rucioAuthCredentials && !selectedInstance && <div className={classes.container}>Loading...</div>}
            </>
          )}
        </div>
      </div>
      <div className={classes.buttonContainer}>
        <Button block onClick={saveSettings}>
          Save Settings
        </Button>
      </div>
    </div>
  );
};

export const Settings = withRequestAPI(_Settings);
