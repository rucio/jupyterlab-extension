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
import { RucioAuthType, RucioUserpassAuth, RucioX509Auth } from '../types';
import { HorizontalHeading } from '../components/HorizontalHeading';
import { TextField } from '../components/TextField';

const useStyles = createUseStyles({
  content: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  },
  scrollable: {
    flex: 1,
    overflow: 'auto',
    paddingTop: '8px'
  },
  container: {
    padding: '8px 16px 8px 16px'
  },
  buttonContainer: {
    extend: 'container',
    borderTop: '1px solid var(--jp-border-color2)'
  },
  instanceName: {
    fontSize: '16pt'
  },
  formControl: {
    marginTop: '8px'
  },
  formItem: {
    marginBottom: '16px'
  },
  label: {
    margin: '4px 0 4px 0'
  },
  textFieldContainer: {
    margin: '8px 0 8px 0'
  },
  warning: {
    margin: '8px 8px 16px 8px',
    color: 'var(--jp-ui-font-color2)',
    fontSize: '9pt'
  },
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  iconText: {
    verticalAlign: 'middle',
    paddingLeft: '4px'
  },
  hidden: {
    display: 'none'
  },
  action: {
    cursor: 'pointer',
    color: 'var(--jp-rucio-primary-blue-color)',
    fontSize: '9pt'
  },
  buttonSavedAcknowledgement: {
    background: '#689f38',
    color: '#ffffff',
    '&:hover': {
      background: '#689f38'
    }
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
  const [rucioUserpassAuthCredentials, setRucioUserpassAuthCredentials] = useState<RucioUserpassAuth>();
  const [rucioX509AuthCredentials, setRucioX509AuthCredentials] = useState<RucioX509Auth>();
  const [credentialsLoading, setCredentialsLoading] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [showSaved, setShowSaved] = useState<boolean>(false);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState<boolean>(false);

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

    return actions.postActiveInstance(instanceName, authType).catch(e => console.log(e));
  };

  const saveSettings = () => {
    const promises = [];
    if (selectedInstance && selectedAuthType) {
      const setActiveInstancePromise = setActiveInstance(selectedInstance, selectedAuthType);
      promises.push(setActiveInstancePromise);
    }

    if (selectedAuthType) {
      const rucioAuthCredentials = selectedAuthType === 'userpass' ? rucioUserpassAuthCredentials : rucioX509AuthCredentials;
      if (rucioAuthCredentials) {
        const setPutAuthConfigPromise = actions.putAuthConfig(selectedInstance, selectedAuthType, rucioAuthCredentials);
        promises.push(setPutAuthConfigPromise);
      }
    }

    setLoading(true);
    Promise.all(promises)
      .then(() => {
        setShowSaved(true);
        setTimeout(() => setShowSaved(false), 3000);
      })
      .finally(() => setLoading(false));
  };

  const reloadAuthConfig = () => {
    if (!selectedInstance) {
      return;
    }

    setCredentialsLoading(true);

    if (selectedAuthType === 'userpass') {
      actions
        .fetchAuthConfig<RucioUserpassAuth>(selectedInstance, selectedAuthType)
        .then(c => setRucioUserpassAuthCredentials(c))
        .catch(() => setRucioUserpassAuthCredentials(undefined))
        .finally(() => setCredentialsLoading(false));
    } else if (selectedAuthType === 'x509') {
      actions
        .fetchAuthConfig<RucioX509Auth>(selectedInstance, selectedAuthType)
        .then(c => setRucioX509AuthCredentials(c))
        .catch(() => setRucioX509AuthCredentials(undefined))
        .finally(() => setCredentialsLoading(false));
    }
  };

  useEffect(reloadAuthConfig, [selectedInstance, selectedAuthType]);

  const settingsComplete = selectedInstance && selectedAuthType;

  const selectStyles = {
    control: (provided: any, state: any) => ({
      ...provided,
      borderRadius: 0,
      borderColor: 'var(--jp-border-color1)',
      background: 'var(--jp-layout-color1)'
    }),
    singleValue: (provided: any, state: any) => ({
      ...provided,
      color: 'var(--jp-ui-font-color1)'
    }),
    menu: (provided: any, state: any) => ({
      ...provided,
      background: 'var(--jp-layout-color1)',
      color: 'var(--jp-ui-font-color1)'
    }),
    option: (provided: any, { isFocused, isSelected }: any) => ({
      ...provided,
      background: isFocused ? (isSelected ? provided.background : 'var(--jp-layout-color2)') : provided.background,
      ':active': {
        ...provided[':active'],
        background: isSelected ? provided.background : 'var(--jp-layout-color2)'
      }
    })
  };

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
          <div className={selectedInstance && selectedAuthType === 'userpass' ? '' : classes.hidden}>
            <HorizontalHeading title="Username &amp; Password" />
            <UserPassAuth
              loading={credentialsLoading}
              params={rucioUserpassAuthCredentials}
              onAuthParamsChange={v => setRucioUserpassAuthCredentials(v)}
            />
          </div>
          <div className={selectedInstance && selectedAuthType === 'x509' ? '' : classes.hidden}>
            <HorizontalHeading title="X.509 User Certificate" />
            <X509Auth
              loading={credentialsLoading}
              params={rucioX509AuthCredentials}
              onAuthParamsChange={v => setRucioX509AuthCredentials(v)}
            />
          </div>
        </div>
        <div className={showAdvancedSettings ? undefined : classes.hidden}>
          <HorizontalHeading title="Advanced Settings" />
          <div className={classes.container}>
            <div className={classes.formItem}>
              <div className={classes.textFieldContainer}>
                <div className={classes.label}>Virtual Organization (VO)</div>
                <TextField placeholder="Virtual Organization" />
                <div className={classes.warning}>
                  If no VO is specified, it is set to the one configured by the site administrator.
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={classes.container}>
          {!showAdvancedSettings && (
            <div className={classes.action} onClick={() => setShowAdvancedSettings(true)}>
              Show Advanced Settings
            </div>
          )}
          {showAdvancedSettings && (
            <div className={classes.action} onClick={() => setShowAdvancedSettings(false)}>
              Hide Advanced Settings
            </div>
          )}
        </div>
      </div>
      <div className={classes.buttonContainer}>
        <Button
          block
          onClick={saveSettings}
          disabled={!settingsComplete || loading}
          outlineColor={!loading && showSaved ? '#689f38' : undefined}
          color={!loading && showSaved ? '#FFFFFF' : undefined}
          className={!loading && showSaved ? classes.buttonSavedAcknowledgement : undefined}
        >
          {!loading && !showSaved && <>Save Settings</>}
          {loading && <>Saving...</>}
          {!loading && showSaved && <>Saved!</>}
        </Button>
      </div>
    </div>
  );
};

export const Settings = withRequestAPI(_Settings);
