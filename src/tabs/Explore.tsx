import React, { useState } from 'react';
import { createUseStyles } from 'react-jss';
import qs from 'querystring';
import { useStoreState } from 'pullstate';
import { UIStore } from '../stores/UIStore';
import { TextField } from '../components/TextField';
import { HorizontalHeading } from '../components/HorizontalHeading';
import { DIDListItem } from '../components/DIDListItem';
import { requestAPI } from '../utils/ApiRequest';
import { Spinning } from '../components/Spinning';

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
  loading: {
    padding: '16px'
  },
  icon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  iconText: {
    verticalAlign: 'middle',
    paddingLeft: '4px'
  }
});

export const Explore: React.FunctionComponent = () => {
  const classes = useStyles();

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResult, setSearchResult] = useState<string[]>();
  const [lastQuery, setLastQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const isDIDContainer =
    !!searchResult &&
    searchResult.length > 0 &&
    !searchResult.includes(lastQuery);

  const query = {
    namespace: activeInstance.name,
    did: searchQuery
  };

  const doSearch = () => {
    setLoading(true);
    setSearchResult(undefined);
    setLastQuery(searchQuery);
    requestAPI<string[]>(`files?${qs.encode(query)}`)
      .then(result => setSearchResult(result))
      .catch(e => setSearchResult([]))
      .finally(() => setLoading(false));
  };

  const searchButton = (
    <div className={classes.searchButton} onClick={doSearch}>
      <i className={`${classes.searchIcon} material-icons`}>search</i>
    </div>
  );

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      doSearch();
    }
  };

  return (
    <div>
      <div className={classes.searchContainer}>
        <TextField
          outlineColor="#E0E0E0"
          placeholder="Enter a Data Identifier (DID)"
          after={searchButton}
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          onKeyPress={handleKeyPress}
        />
      </div>
      {loading && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>
            hourglass_top
          </Spinning>
          <span className={classes.iconText}>Loading...</span>
        </div>
      )}
      {!!searchResult && (
        <>
          <HorizontalHeading title="Search Results" />
          <div className={classes.resultsContainer}>
            {isDIDContainer && (
              <DIDListItem type="container" did={lastQuery} key={lastQuery} />
            )}
            {searchResult.map(did => (
              <DIDListItem type="file" did={did} key={did} />
            ))}
          </div>
          {!!searchResult && searchResult.length === 0 && (
            <div className={classes.loading}>No results found</div>
          )}
        </>
      )}
    </div>
  );
};
