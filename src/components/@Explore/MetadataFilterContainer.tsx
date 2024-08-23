import React from 'react';
import { createUseStyles } from 'react-jss';
import {
  IMetadataFilter,
  MetadataFilterItem
} from '../components/../@Explore/MetadataFilterItem';

const useStyles = createUseStyles({
  metadataFilterContainer: {},
  addMetadataFilterButton: {
    marginTop: '4px',
    marginRight: '16px',
    marginLeft: '16px',
    width: 'fit-content',
    fontSize: '9pt',
    cursor: 'pointer',
    opacity: 0.5,
    '&:hover': {
      opacity: 1
    }
  },
  deleteFiltersButton: {
    marginTop: '4px',
    marginRight: '16px',
    marginLeft: '16px',
    width: 'fit-content',
    display: 'flex',
    alignItems: 'center',
    fontSize: '9pt',
    cursor: 'pointer',
    opacity: 0.5,
    '&:hover': {
      opacity: 1
    }
  },
  deleteFiltersIcon: {
    fontSize: '9pt',
    cursor: 'pointer',
    opacity: 0.5,
    '&:hover': {
      opacity: 1
    }
  }
});

export interface IMetadataFilterContainer {
  onKeyPress: (e: React.KeyboardEvent<HTMLInputElement>) => any;
  metadataFilters: IMetadataFilter[];
  setMetadataFilters: React.Dispatch<React.SetStateAction<IMetadataFilter[]>>;
}

export const MetadataFilterContainer: React.FunctionComponent<
  IMetadataFilterContainer
> = ({ onKeyPress, metadataFilters, setMetadataFilters }) => {
  const classes = useStyles();

  const handleAddMetadataFilter = () => {
    setMetadataFilters([
      ...metadataFilters,
      { logic: 'And', key: '', operator: '=', value: '' }
    ]);
  };

  const handleDeleteMetadataFilter = (indexToDelete: number) => {
    setMetadataFilters(prev => {
      const newFilters = prev.filter((_, index) => index !== indexToDelete);
      if (indexToDelete === 0 && newFilters.length > 0) {
        newFilters[0] = { ...newFilters[0], logic: 'And' };
      }
      return newFilters;
    });
  };

  const handleDeleteAllMetadataFilters = () => {
    setMetadataFilters([]);
  };

  const handleFilterChange = (
    index: number,
    updatedFilter: IMetadataFilter
  ) => {
    setMetadataFilters(prev => {
      const newFilters = [...prev];
      newFilters[index] = updatedFilter;
      return newFilters;
    });
  };

  return (
    <div className={classes.metadataFilterContainer}>
      {!metadataFilters.length && (
        <div
          className={classes.addMetadataFilterButton}
          onClick={handleAddMetadataFilter}
        >
          + Add metadata filter
        </div>
      )}
      {metadataFilters.map((filter, index) => (
        <MetadataFilterItem
          key={index}
          filter={filter}
          showBoolOperatorDropdown={index === 0}
          onDelete={() => handleDeleteMetadataFilter(index)}
          onChange={updatedFilter => handleFilterChange(index, updatedFilter)}
          onKeyPress={onKeyPress}
        />
      ))}
      {!!metadataFilters.length && (
        <div
          className={classes.addMetadataFilterButton}
          onClick={handleAddMetadataFilter}
        >
          + Add filter rule
        </div>
      )}
      {!!metadataFilters.length && (
        <div
          className={classes.deleteFiltersButton}
          onClick={handleDeleteAllMetadataFilters}
        >
          <i className={`${classes.deleteFiltersIcon} material-icons`}>
            delete
          </i>
          <span style={{ marginLeft: '8px' }}>Delete filter</span>
        </div>
      )}
    </div>
  );
};
