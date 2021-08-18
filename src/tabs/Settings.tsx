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

import React, { useMemo, useState, useEffect } from 'react';
import { createUseStyles } from 'react-jss';
import Select from 'react-select';
import { useStoreState } from 'pullstate';
import { UIStore, resetRucioCaches } from '../stores/UIStore';
import { Button } from '../components/Button';
import { withRequestAPI, WithRequestAPIProps } from '../utils/Actions';
import { UserPassAuth } from '../components/@Settings/UserPassAuth';
import { X509Auth } from '../components/@Settings/X509Auth';
import { X509ProxyAuth } from '../components/@Settings/X509ProxyAuth';
import { Instance, RucioAuthType, RucioUserpassAuth, RucioX509Auth, RucioX509ProxyAuth } from '../types';
import { HorizontalHeading } from '../components/HorizontalHeading';

const getEnabledAuthTypes = (instance: Instance) =>
  [
    instance.oidcEnabled ? { label: 'OpenID Connect', value: 'oidc' } : undefined,
    { label: 'X.509 User Certificate', value: 'x509' },
    { label: 'X.509 Proxy Certificate', value: 'x509_proxy' },
    { label: 'Username & Password', value: 'userpass' }
  ].filter(x => !!x) as Array<{ label: string; value: string }>;

const useStyles = createUseStyles({
  content: {
    height: '100%',
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column'
  },
  scrollable: {
    flex: 1,
    paddingTop: '8px'
  },
  container: {
    padding: '8px 16px 8px 16px'
  },
  buttonContainer: {
    extend: 'container'
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
  subtitle: {
    color: 'var(--jp-ui-font-color2)',
    fontSize: '9pt'
  },
  warning: {
    extend: 'subtitle',
    margin: '8px 8px 16px 8px'
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
  },
  buttonPurgedAcknowledgement: {
    extend: 'purgeButton',
    background: 'var(--jp-error-color1)',
    color: '#ffffff',
    '&:hover': {
      background: 'var(--jp-error-color1)'
    }
  },
  purgeButton: {
    marginTop: '16px'
  }
});

const _Settings: React.FunctionComponent = props => {
  const { actions } = props as WithRequestAPIProps;

  const classes = useStyles();
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);
  const activeAuthType = useStoreState(UIStore, s => s.activeAuthType);
  const instances = useStoreState(UIStore, s => s.instances) || [];

  const [selectedInstance, setSelectedInstance] = useState<string | undefined>(activeInstance?.name);

  const selectedInstanceObject = useMemo(
    () => instances.find(i => i.name === activeInstance?.name),
    [instances, activeInstance]
  );

  const authTypeOptions = selectedInstanceObject ? getEnabledAuthTypes(selectedInstanceObject) : [];
  const authTypeDefaultValue = activeAuthType ? authTypeOptions.find(o => o.value === activeAuthType) : undefined;
  const [selectedAuthType, setSelectedAuthType] = useState<RucioAuthType | undefined>(activeAuthType);

  const [rucioUserpassAuthCredentials, setRucioUserpassAuthCredentials] = useState<RucioUserpassAuth>();
  const [rucioX509AuthCredentials, setRucioX509AuthCredentials] = useState<RucioX509Auth>();
  const [rucioX509ProxyAuthCredentials, setRucioX509ProxyAuthCredentials] = useState<RucioX509ProxyAuth>();
  const [credentialsLoading, setCredentialsLoading] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [showSaved, setShowSaved] = useState<boolean>(false);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState<boolean>(false);
  const [purgingCache, setPurgingCache] = useState<boolean>(false);
  const [showCachePurged, setShowCachePurged] = useState<boolean>(false);

  const instanceOptions = useMemo(() => instances?.map(i => ({ label: i.displayName, value: i.name })), [instances]);

  const setActiveInstance = (instanceName: string, authType: RucioAuthType) => {
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
    if (!selectedInstance) {
      return;
    }

    const promises = [];
    if (selectedInstance && selectedAuthType) {
      const setActiveInstancePromise = setActiveInstance(selectedInstance, selectedAuthType);
      promises.push(setActiveInstancePromise);
    }

    if (selectedAuthType) {
      const rucioAuthCredentials = (() => {
        switch (selectedAuthType) {
          case 'userpass':
            return rucioUserpassAuthCredentials;
          case 'x509':
            return rucioX509AuthCredentials;
          case 'x509_proxy':
            return rucioX509ProxyAuthCredentials;
        }
      })();

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
    } else if (selectedAuthType === 'x509_proxy') {
      actions
        .fetchAuthConfig<RucioX509ProxyAuth>(selectedInstance, selectedAuthType)
        .then(c => setRucioX509ProxyAuthCredentials(c))
        .catch(() => setRucioX509ProxyAuthCredentials(undefined))
        .finally(() => setCredentialsLoading(false));
    }
  };

  const purgeCache = () => {
    setShowCachePurged(false);
    setPurgingCache(true);
    actions
      .purgeCache()
      .then(() => {
        setShowCachePurged(true);
        setTimeout(() => setShowCachePurged(false), 3000);
      })
      .finally(() => setPurgingCache(false));
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

  const instanceDefaultValue = activeInstance ? { label: activeInstance.displayName, value: activeInstance.name } : null;

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
              onChange={(value: any) => setSelectedInstance(value.value)}
            />
          </div>
          <div className={classes.formItem}>
            <div className={classes.label}>Authentication</div>
            <Select
              className={classes.formControl}
              options={authTypeOptions}
              styles={selectStyles}
              defaultValue={authTypeDefaultValue}
              onChange={(value: any) => setSelectedAuthType(value.value)}
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
          <div className={selectedInstance && selectedAuthType === 'x509_proxy' ? '' : classes.hidden}>
            <HorizontalHeading title="X.509 Proxy Certificate" />
            <X509ProxyAuth
              loading={credentialsLoading}
              params={rucioX509ProxyAuthCredentials}
              onAuthParamsChange={v => setRucioX509ProxyAuthCredentials(v)}
            />
          </div>
        </div>
        <div className={showAdvancedSettings ? undefined : classes.hidden}>
          <HorizontalHeading title="Advanced Settings" />
          <div className={classes.container}>
            <div className={classes.formItem}>
              <div className={classes.textFieldContainer}>
                <div className={classes.label}>Purge cache</div>
                <div className={classes.subtitle}>Remove all caches, including search results and DID paths.</div>
                <Button
                  block
                  onClick={purgeCache}
                  disabled={purgingCache}
                  outlineColor="var(--jp-error-color1)"
                  color={!purgingCache && showCachePurged ? '#FFFFFF' : 'var(--jp-error-color1)'}
                  className={!purgingCache && showCachePurged ? classes.buttonPurgedAcknowledgement : classes.purgeButton}
                >
                  {!purgingCache && !showCachePurged && <>Purge Cache</>}
                  {purgingCache && <>Purging...</>}
                  {!purgingCache && showCachePurged && <>Purged!</>}
                </Button>
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
