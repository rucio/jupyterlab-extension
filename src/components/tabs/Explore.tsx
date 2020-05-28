import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../TextField';
import { HorizontalHeading } from '../HorizontalHeading';
import { DIDListItem } from '../DIDListItem';

const useStyles = createUseStyles({
  searchContainer: {
    padding: '8px'
  },
  resultsContainer: {},
  searchButton: {
    alignItems: 'center',
    padding: '4px',
    lineHeight: 0,
    cursor: 'pointer'
  },
  searchIcon: {
    color: '#2196F3'
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
