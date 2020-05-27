import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';
import Select from 'react-select';

const useStyles = createUseStyles({
  heading: {
    fontWeight: 'bold',
    padding: '24px 8px 4px 8px',
    fontSize: '10pt',
    textTransform: 'uppercase'
  },
  container: {
    padding: '8px'
  }
});

const selectStyles = {
  control: (provided: any) => ({
    ...provided,
    borderRadius: 0
  })
};

const options = [
  { value: 'atlas', label: 'ATLAS' },
  { value: 'cms', label: 'CMS' },
  { value: 'alice', label: 'ALICE' },
  { value: 'lhcb', label: 'LHCb' }
];

export const Settings: React.FunctionComponent = () => {
  const classes = useStyles();
  const [rucioInstance, setRucioInstance] = useState<any>();

  return (
    <div>
      <div className={classes.heading}>Rucio Instance</div>
      <div className={classes.container}>
        <Select
          value={rucioInstance}
          onChange={v => setRucioInstance(v)}
          options={options}
          styles={selectStyles}
        />
      </div>
    </div>
  );
};
