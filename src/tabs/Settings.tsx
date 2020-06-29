import React, { useMemo, useState } from 'react';
import { createUseStyles } from 'react-jss';
import Select from 'react-select';
import { useStoreState } from 'pullstate';
import { UIStore, resetRucioCaches } from '../stores/UIStore';
import { Button } from '../components/Button';
import { withRequestAPI, WithRequestAPIProps } from '../utils/Actions';
import { authTypeOptions } from '../const';
import { UserPassAuth } from '../components/@Settings/UserPassAuth';
import { X509Auth } from '../components/@Settings/X509Auth';

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
  const [selectedAuthType, setSelectedAuthType] = useState<string>();

  const instanceOptions = useMemo(() => instances?.map(i => ({ label: i.displayName, value: i.name })), [instances]);

  const instanceSettingsChanged = activeInstance?.name !== selectedInstance;
  const settingsChanged = instanceSettingsChanged;

  const setActiveInstance = (value?: string) => {
    resetRucioCaches();

    UIStore.update(s => {
      const instance = instances.find(i => i.name === value);
      s.activeInstance = instance;
    });

    actions.postActiveInstance(value).catch(e => console.log(e));
  };

  const saveSettings = () => {
    if (instanceSettingsChanged) {
      setActiveInstance(selectedInstance);
    }
  };

  const selectStyles = {
    control: (provided: any, state: any) => ({
      ...provided,
      borderRadius: 0
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
              onChange={(value: any) => {
                setSelectedAuthType(value.value);
              }}
            />
          </div>
        </div>
        <div>
          {selectedAuthType === 'userpass' && <UserPassAuth />}
          {selectedAuthType === 'x509' && <X509Auth />}
        </div>
      </div>
      <div className={classes.buttonContainer}>
        <Button block disabled={!settingsChanged} onClick={saveSettings}>
          Save Changes
        </Button>
      </div>
    </div>
  );
};

export const Settings = withRequestAPI(_Settings);
