import React from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { ExtensionStore } from '../stores/ExtensionStore';
import { TextField } from '../components/TextField';
import { HorizontalHeading } from '../components/HorizontalHeading';
import { DIDListItem } from '../components/DIDListItem';
import { InlineDropdown } from '../components/InlineDropdown';
import { searchByOptions } from '../const';

const useStyles = createUseStyles({
  searchContainer: {
    padding: '8px'
  },
  resultsContainer: {},
  filterContainer: {
    padding: '0 16px 0 16px',
    fontSize: '9pt'
  },
  searchButton: {
    alignItems: 'center',
    padding: '4px',
    lineHeight: 0,
    cursor: 'pointer'
  },
  searchIcon: {
    color: '#2196F390',
    '&:hover': {
      color: '#2196F3'
    }
  },
  dropdown: {
    color: '#2196F3',
    cursor: 'pointer',
    marginLeft: '4px'
  },
  listItem: {
    borderBottom: '1px solid #E0E0E0',
    padding: '8px 16px 8px 16px',
    cursor: 'pointer',
    'background-size': 'auto 50%',
    'background-position': 'right 16px center',
    backgroundRepeat: 'no-repeat',
    '&:last-child': {
      borderBottom: 'none'
    },
    '&:hover': {
      backgroundColor: '#eeeeee'
    }
  }
});

export const Explore: React.FunctionComponent = () => {
  const classes = useStyles();

  const searchBy = useStoreState(ExtensionStore, s => s.searchBy);
  const setSearchBy = (value: string) => {
    ExtensionStore.update(s => {
      s.searchBy = value;
    });
  };

  const searchButton = (
    <div className={classes.searchButton}>
      <i className={`${classes.searchIcon} material-icons`}>search</i>
    </div>
  );

  return (
    <div>
      <div className={classes.searchContainer}>
        <TextField
          outlineColor="#E0E0E0"
          placeholder="Enter a Data Identifier (DID)"
          after={searchButton}
        />
      </div>
      <div className={classes.filterContainer}>
        Search by
        <InlineDropdown
          className={classes.dropdown}
          options={searchByOptions}
          value={searchBy}
          onItemSelected={setSearchBy}
          optionWidth="170px"
        />
      </div>
      <HorizontalHeading title="Search Results" />
      <div className={classes.resultsContainer}>
        <DIDListItem type="container" did="atlas.2d:lhc.sensor2.34eafd" />
        <DIDListItem type="container" did="atlas.2d:lhc.sensor2.34eafd" />
        <DIDListItem type="dataset" did="atlas.2d:lhc.sensor2.34eafd" />
        <DIDListItem type="file" did="atlas.2d:lhc.sensor2.34eafd" />
        <DIDListItem type="file" did="atlas.2d:lhc.sensor2.34eafd" />
      </div>
    </div>
  );
};
