import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../../components/TextField';

const useStyles = createUseStyles({
  control: {
    display: "flex",
    flexDirection: "row",
    alignItems: "stretch",
    position: "relative",
    marginBottom: "8px",
  },
  deleteButton: {
    fontSize: '9pt',
    cursor: 'pointer',
    opacity: 0.5,
    '&:hover': {
      opacity: 1
    }
  },
  deleteIcon: {
    fontSize: '9pt',
    cursor: 'pointer',
    opacity: 0.5,
    '&:hover': {
      opacity: 1
    }
  },
})

const operators = ["=", "≠", "<", ">", "≤", "≥"];

export interface MetadataFilter {
  logic: string;
  key: string;
  operator: string;
  value: string;
}

export interface MetadataFilterItemProps {
  filter: MetadataFilter;
  showBoolOperatorDropdown: boolean;
  onDelete: () => any;
  onChange: (updatedFilter: MetadataFilter) => any;
}

export const MetadataFilterItem: React.FC<MetadataFilterItemProps> = ({
  filter,
  showBoolOperatorDropdown,
  onDelete,
  onChange,
}) => {
  const classes = useStyles();

  const handleLogicChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange({ ...filter, logic: e.target.value });
  };

  const handleKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filter, key: e.target.value });
  };

  const handleOperatorChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange({ ...filter, operator: e.target.value });
  };

  const handleValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filter, value: e.target.value });
  };

  return (
    <div className={classes.control}>
      {showBoolOperatorDropdown ? (
        <div>Where</div>
      ) : (
        <select value={filter.logic} onChange={handleLogicChange}>
          <option value="And">And</option>
          <option value="Or">Or</option>
        </select>
      )}
      <TextField
        placeholder="Key"
        value={filter.key}
        onChange={handleKeyChange}
      />
      <select value={filter.operator} onChange={handleOperatorChange}>
        {operators.map((op) => (
          <option key={op} value={op}>
            {op}
          </option>
        ))}
      </select>
      <TextField
        placeholder="Value"
        value={filter.value}
        onChange={handleValueChange}
      />
      <div className={classes.deleteButton} onClick={onDelete}>
        <i className={`${classes.deleteIcon} material-icons`}>delete</i>
      </div>
    </div>
  );
};
