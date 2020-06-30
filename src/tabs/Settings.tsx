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
import { Spinning } from '../components/Spinning';

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

const _Settings: React.FunctionComponent = props => {
  const { actions } = props as WithRequestAPIProps;

  const classes = useStyles();
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);
  const activeAuthType = useStoreState(UIStore, s => s.activeAuthType);
  const instances = useStoreState(UIStore, s => s.instances) || [];

  const instanceDefaultValue = activeInstance ? { label: activeInstance.displayName, value: activeInstance.name } : null;
  const authTypeDefaultValue = activeAuthType ? authTypeOptions.find(o => o.value === activeAuthType) : null;

  const [selectedInstance, setSelectedInstance] = useState<string>(instanceDefaultValue?.value);
  const [selectedAuthType, setSelectedAuthType] = useState<RucioAuthType>(activeAuthType);
  const [rucioAuthCredentials, setRucioAuthCredentials] = useState<RucioAuthCredentials>();
  const [credentialsLoading, setCredentialsLoading] = useState<boolean>(true);

  const instanceOptions = useMemo(() => instances?.map(i => ({ label: i.displayName, value: i.name })), [instances]);

  const setActiveInstance = (instanceName?: string, authType?: RucioAuthType) => {
    UIStore.update(s => {
      if (s.activeInstance?.name !== instanceName) {
        resetRucioCaches();
        const instance = instances.find(i => i.name === instanceName);
        s.activeInstance = instance;
      }

      if (s.activeAuthType !== authType) {
        s.activeAuthType = authType;
      }
    });

    actions.postActiveInstance(instanceName, authType).catch(e => console.log(e));
  };

  const setRucioAuthConfig = (namespace: string, authType: RucioAuthType, rucioAuthCredentials: RucioAuthCredentials) => {
    actions.putAuthConfig(namespace, authType, rucioAuthCredentials);
  };

  const saveSettings = () => {
    if (selectedInstance && selectedAuthType) {
      setActiveInstance(selectedInstance, selectedAuthType);
    }

    if (!!selectedAuthType && !!rucioAuthCredentials) {
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

    setCredentialsLoading(true);
    actions
      .getAuthConfig<any>(selectedInstance, selectedAuthType)
      .then(c => setRucioAuthCredentials(c))
      .catch(() => setRucioAuthCredentials(undefined))
      .finally(() => setCredentialsLoading(false));
  };

  useEffect(reloadAuthConfig, [selectedInstance, selectedAuthType]);

  const settingsComplete = selectedInstance && selectedAuthType;

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
              defaultValue={authTypeDefaultValue}
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
              {!credentialsLoading && (
                <UserPassAuth params={rucioAuthCredentials as RucioUserpassAuth} onChange={v => setRucioAuthCredentials(v)} />
              )}
              {credentialsLoading && (
                <div className={classes.container}>
                  <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
                  <span className={classes.iconText}>Loading...</span>
                </div>
              )}
            </>
          )}
          {selectedAuthType === 'x509' && !!selectedInstance && (
            <>
              <HorizontalHeading title="X.509 User Certificate" />
              {!credentialsLoading && (
                <X509Auth params={rucioAuthCredentials as RucioX509Auth} onChange={v => setRucioAuthCredentials(v)} />
              )}
              {credentialsLoading && (
                <div className={classes.container}>
                  <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
                  <span className={classes.iconText}>Loading...</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>
      <div className={classes.buttonContainer}>
        <Button block onClick={saveSettings} disabled={!settingsComplete}>
          Save Settings
        </Button>
      </div>
    </div>
  );
};

export const Settings = withRequestAPI(_Settings);
