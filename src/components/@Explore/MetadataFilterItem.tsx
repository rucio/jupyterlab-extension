import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../../components/TextField';

const useStyles = createUseStyles({
  metadataFilter: {
    display: 'flex',
    flexWrap: 'nowrap',
    flexDirection: 'row',
    alignItems: 'center',
    position: 'relative',
    padding: '4px 16px 0 16px'
  },
  where: {
    marginRight: '5pt'
  },
  select: {
    display: 'flex',
    alignSelf: 'stretch',
    color: 'var(--jp-ui-font-color1)',
    background: 'var(--jp-layout-color1)'
  },
  key: {
    flex: 1,
    minWidth: 0
  },
  value: {
    marginRight: '4px',
    flex: 1,
    minWidth: 0
  },
  deleteButton: {
    fontSize: '13pt',
    cursor: 'pointer',
    opacity: 0.5,
    '&:hover': {
      opacity: 1
    }
  },
  deleteIcon: {
    fontSize: '13pt',
    cursor: 'pointer',
    opacity: 0.5,
    '&:hover': {
      opacity: 1
    }
  }
});

const operators = ['=', '≠', '<', '>', '≤', '≥'];

export interface IMetadataFilter {
  logic: string;
  key: string;
  operator: string;
  value: string;
}

export interface IMetadataFilterItemProps {
  filter: IMetadataFilter;
  showBoolOperatorDropdown: boolean;
  onDelete: () => any;
  onChange: (updatedFilter: IMetadataFilter) => any;
  onKeyPress: (e: React.KeyboardEvent<HTMLInputElement>) => any;
}

export const MetadataFilterItem: React.FC<IMetadataFilterItemProps> = ({
  filter,
  showBoolOperatorDropdown,
  onDelete,
  onChange,
  onKeyPress
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
    <div className={classes.metadataFilter}>
      {showBoolOperatorDropdown ? (
        <div className={classes.where}>
          <div>Where</div>
        </div>
      ) : (
        <select
          className={classes.select}
          value={filter.logic}
          onChange={handleLogicChange}
        >
          <option value="And">And</option>
          <option value="Or">Or</option>
        </select>
      )}
      <div className={classes.key}>
        <TextField
          placeholder="Key"
          value={filter.key}
          onChange={handleKeyChange}
          onKeyPress={onKeyPress}
        />
      </div>
      <select
        className={classes.select}
        value={filter.operator}
        onChange={handleOperatorChange}
      >
        {operators.map(op => (
          <option key={op} value={op}>
            {op}
          </option>
        ))}
      </select>
      <div className={classes.value}>
        <TextField
          placeholder="Value"
          value={filter.value}
          onChange={handleValueChange}
          onKeyPress={onKeyPress}
        />
      </div>
      <div className={classes.deleteButton} onClick={onDelete}>
        <i className={`${classes.deleteIcon} material-icons`}>delete</i>
      </div>
    </div>
  );
};
