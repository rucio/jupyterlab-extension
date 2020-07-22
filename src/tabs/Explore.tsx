import React, { useState, useEffect } from 'react';
import { createUseStyles } from 'react-jss';
import { useStoreState } from 'pullstate';
import { UIStore } from '../stores/UIStore';
import { TextField } from '../components/TextField';
import { HorizontalHeading } from '../components/HorizontalHeading';
import { DIDListItem } from '../components/@Explore/DIDListItem';
import { Spinning } from '../components/Spinning';
import { withRequestAPI, WithRequestAPIProps } from '../utils/Actions';
import { DIDSearchType, DIDSearchResult } from '../types';
import { InlineDropdown } from '../components/InlineDropdown';

const useStyles = createUseStyles({
  searchContainer: {
    padding: '8px'
  },
  filterContainer: {
    padding: '0 16px 0 16px',
    fontSize: '9pt'
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

const searchByOptions = [
  { title: 'Datasets or Containers', value: 'collection' },
  { title: 'Datasets', value: 'dataset' },
  { title: 'Containers', value: 'container' },
  { title: 'Files', value: 'file' },
  { title: 'All', value: 'all' }
];

const _Explore: React.FunctionComponent = props => {
  const classes = useStyles();

  const { actions } = props as WithRequestAPIProps;

  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<DIDSearchType>('collection');
  const [searchResult, setSearchResult] = useState<DIDSearchResult[]>();
  const [error, setError] = useState<string>();
  const [lastQuery, setLastQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const doSearch = () => {
    setLastQuery(searchQuery);
  };

  const itemsSortFunction = (a: DIDSearchResult, b: DIDSearchResult): number => {
    if (a.type === b.type) {
      return a.did.toLowerCase() < b.did.toLowerCase() ? -1 : 1;
    }

    if (a.type === 'container' && b.type === 'dataset') {
      return -1;
    }

    if ((a.type === 'container' || a.type === 'dataset') && b.type === 'file') {
      return -1;
    }

    return 0;
  };

  useEffect(() => {
    if (!lastQuery) {
      return;
    }

    setLoading(true);
    setSearchResult(undefined);
    setError(undefined);
    actions
      .searchDID(activeInstance.name, searchQuery, searchType)
      .then(items => items.sort(itemsSortFunction))
      .then(result => setSearchResult(result))
      .catch(e => {
        setSearchResult([]);
        if (e.response.status === 401) {
          setError('Authentication error. Perhaps you set an invalid credential?');
          return;
        }

        if (e.response.status === 400) {
          const body = e.response.json();
          if (body.error === 'wildcard_disabled') {
            setError('Wildcard search is disabled.');
            return;
          }
        }
      })
      .finally(() => setLoading(false));
  }, [lastQuery, searchType]);

  const searchButton = (
    <div className={classes.searchButton} onClick={() => setLastQuery(searchQuery)}>
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
      <div className={classes.filterContainer}>
        Search
        <InlineDropdown
          className={classes.dropdown}
          options={searchByOptions}
          value={searchType}
          onItemSelected={setSearchType}
          optionWidth="180px"
        />
      </div>
      {loading && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
          <span className={classes.iconText}>Loading...</span>
        </div>
      )}
      {!!searchResult && (
        <>
          <HorizontalHeading title="Search Results" />
          <div className={classes.resultsContainer}>
            {searchResult.map(did => (
              <DIDListItem type={did.type} did={did.did} size={did.size} key={did.did} />
            ))}
          </div>
          {((!!searchResult && searchResult.length === 0) || !!error) && (
            <div className={classes.loading}>{error || 'No results found'}</div>
          )}
        </>
      )}
    </div>
  );
};

export const Explore = withRequestAPI(_Explore);
