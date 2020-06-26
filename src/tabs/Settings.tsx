import React, { useMemo, useState } from 'react';
import { createUseStyles } from 'react-jss';
import Select from 'react-select';
import { useStoreState } from 'pullstate';
import { UIStore, resetRucioCaches } from '../stores/UIStore';
import { HorizontalHeading } from '../components/HorizontalHeading';
import { Button } from '../components/Button';
import { withRequestAPI, WithRequestAPIProps } from '../utils/Actions';

const useStyles = createUseStyles({
  container: {
    padding: '16px'
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

  const instanceOptions = useMemo(() => instances?.map(i => ({ label: i.displayName, value: i.name })), [instances]);
  const authTypeOptions = [
    { label: 'Username & Password', value: 'userpass' },
    { label: 'X.509 User Certificate', value: 'x509' }
  ];

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
    <>
      <div className={classes.container}>
        <div className={classes.formItem}>
          <div className={classes.label}>Active Instance</div>
          <Select
            className={classes.formControl}
            defaultValue={instanceDefaultValue}
            options={instanceOptions}
            styles={selectStyles}
            onChange={(value: any) => {
              setSelectedInstance(value.value);
            }}
          />
        </div>
        <div className={classes.formItem}>
          <div className={classes.label}>Rucio Authentication</div>
          <Select className={classes.formControl} options={authTypeOptions} styles={selectStyles} />
        </div>
      </div>
      <div>
        <HorizontalHeading title="X.509 User Certificate" />
      </div>
      <div className={classes.container}>
        <Button block disabled={!settingsChanged} onClick={saveSettings}>
          Save Settings
        </Button>
      </div>
    </>
  );
};

export const Settings = withRequestAPI(_Settings);
