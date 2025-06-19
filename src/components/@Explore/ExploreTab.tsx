/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021
 */

import React, { useState, useEffect, useRef } from 'react';
import { createUseStyles } from 'react-jss';
import { VariableSizeList } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import { useStoreState } from 'pullstate';
import { UIStore } from '../../stores/UIStore';
import { TextField } from '../../components/TextField';
import { HorizontalHeading } from '../../components/HorizontalHeading';
import { DIDListItem } from '../../components/@Explore/DIDListItem';
import { Spinning } from '../../components/Spinning';
import { withRequestAPI, IWithRequestAPIProps } from '../../utils/Actions';
import { DIDSearchType, IDIDSearchResult } from '../../types';
import { InlineDropdown } from '../components/../@Explore/InlineDropdown';
import { ListScopesPopover } from '../components/../@Explore/ListScopesPopover';
import { MetadataFilterContainer } from '../components/../@Explore/MetadataFilterContainer';
import { IMetadataFilter } from '../components/../@Explore/MetadataFilterItem';

const useStyles = createUseStyles({
  mainContainer: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden'
  },
  searchContainer: {
    padding: '8px'
  },
  filterContainer: {
    padding: '0 16px 0 16px',
    fontSize: '9pt'
  },
  resultsContainer: {
    flex: 1
  },
  searchButton: {
    alignItems: 'center',
    padding: '8px 8px 8px 4px',
    lineHeight: 0,
    cursor: 'pointer'
  },
  searchIcon: {
    fontSize: '18px',
    color: 'var(--jp-rucio-primary-blue-color)',
    opacity: 0.5,
    '&:hover': {
      opacity: 1
    }
  },
  listScopesButton: {
    alignItems: 'center',
    padding: '8px 4px 8px 4px',
    lineHeight: 0,
    cursor: 'pointer'
  },
  listScopesIcon: {
    fontSize: '18px',
    color: 'var(--jp-layout-color4)',
    opacity: 0.5,
    '&:hover': {
      opacity: 1
    }
  },
  dropdown: {
    color: 'var(--jp-rucio-primary-blue-color)',
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
  },
  errorText: {
    padding: '16px',
    color: 'red',
    flex: 1
  }
});

const searchByOptions = [
  { title: 'Everything', value: 'all' },
  { title: 'Datasets and Containers', value: 'collection' },
  { title: 'Datasets', value: 'dataset' },
  { title: 'Containers', value: 'container' },
  { title: 'Files', value: 'file' }
];

const _Explore: React.FunctionComponent = props => {
  const classes = useStyles();

  const { actions } = props as IWithRequestAPIProps;

  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<DIDSearchType>('all');
  const [searchResult, setSearchResult] = useState<IDIDSearchResult[]>();
  const [didExpanded, setDidExpanded] = useState<{ [index: number]: boolean }>(
    {}
  );
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [searchTrigger, setSearchTrigger] = useState(0);
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);
  const [metadataFilters, setMetadataFilters] = React.useState<
    IMetadataFilter[]
  >([]);

  const doSearch = () => {
    setSearchTrigger(prev => prev + 1); // Increment the counter to trigger the search
  };

  const buildMetadataFilterString = () => {
    return metadataFilters
      .map((filter, index) => {
        const logic = index === 0 ? '' : filter.logic === 'And' ? ',' : ';';
        return `${logic}${filter.key}${filter.operator}${filter.value}`;
      })
      .join('');
  };

  const itemsSortFunction = (
    a: IDIDSearchResult,
    b: IDIDSearchResult
  ): number => {
    if (a.type === b.type) {
      return a.did.toLowerCase() < b.did.toLowerCase() ? -1 : 1;
    }

    if (a.type === 'container' && b.type === 'dataset') {
      return -1;
    }

    if ((a.type === 'container' || a.type === 'dataset') && b.type === 'file') {
      return -1;
    }

    return 1;
  };

  useEffect(() => {
    if (!searchQuery || !activeInstance) {
      return;
    }

    setLoading(true);
    setSearchResult(undefined);
    setDidExpanded({});
    setError(undefined);
    const filterString = buildMetadataFilterString();
    actions
      .searchDID(activeInstance.name, searchQuery, searchType, filterString)
      .then(items => items.sort(itemsSortFunction))
      .then(result => setSearchResult(result))
      .catch(e => {
        setSearchResult([]);

        // The error 'e' is the rich ResponseError object from requestAPI
        if (e.response && e.response.status === 401) {
          setError(
            'Authentication error. Perhaps you set an invalid credential?'
          );
          return;
        }

        // The backend error message is directly available on e.error
        if (e.error) {
          setError(e.error);
        } else {
          // Fallback to the general error message if e.error is not present
          setError(e.message || 'An unknown error occurred.');
        }
      })
      .finally(() => setLoading(false));
  }, [searchTrigger, searchType]);

  const searchBoxRef = useRef<any>(null);
  const onScopeClicked = (scope: string) => {
    setSearchQuery(scope + ':');
    searchBoxRef?.current?.focus();
  };

  const listScopesButton = (
    <ListScopesPopover onScopeClicked={onScopeClicked} key="list-scopes-button">
      <div className={classes.listScopesButton}>
        <i className={`${classes.listScopesIcon} material-icons`}>topic</i>
      </div>
    </ListScopesPopover>
  );

  const searchButton = (
    <div
      className={classes.searchButton}
      onClick={doSearch}
      key="search-button"
    >
      <i className={`${classes.searchIcon} material-icons`}>search</i>
    </div>
  );

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      doSearch();
    }
  };

  const listRef = useRef<VariableSizeList>(null);

  const toggleExpand = (index: number) => {
    listRef.current?.resetAfterIndex(index);
    didExpanded[index] = !didExpanded[index];
    setDidExpanded(didExpanded);
  };

  const getItemHeight = (i: number) => (didExpanded[i] === true ? 64 : 32);

  const Row = ({ index, style }: any) => {
    if (!searchResult) {
      return <></>;
    }

    const item = searchResult[index];
    const expanded = !!didExpanded[index];
    return (
      <DIDListItem
        style={style}
        type={item.type}
        did={item.did}
        size={item.size}
        key={item.did}
        expand={expanded}
        onClick={() => toggleExpand(index)}
      />
    );
  };

  return (
    <div className={classes.mainContainer}>
      <div className={classes.searchContainer}>
        <TextField
          placeholder="Enter a Data Identifier (DID)"
          after={[listScopesButton, searchButton]}
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          autoComplete="off"
          ref={searchBoxRef}
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
      <MetadataFilterContainer
        onKeyPress={handleKeyPress}
        metadataFilters={metadataFilters}
        setMetadataFilters={setMetadataFilters}
      />
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
          {/* The heading can be shown as soon as a search is attempted or an error occurs */}
          {!error && !!searchResult && (
            <HorizontalHeading title="Search Results" />
          )}
          {!!error && <HorizontalHeading title="Error(s) found" />}

          {/* Priority 1: Display the error if it exists */}
          {!!error && <div className={classes.errorText}>{error}</div>}

          {/* Priority 2: If no error, check for search results */}
          {!error && searchResult && (
            <>
              {/* Case A: No results were found */}
              {searchResult.length === 0 && (
                <div className={classes.loading}>No results found</div>
              )}

              {/* Case B: Results were found, display the list */}
              {searchResult.length > 0 && (
                <div className={classes.resultsContainer}>
                  <AutoSizer disableWidth>
                    {({ height }: { height: number }) => (
                      <VariableSizeList
                        ref={listRef}
                        height={height}
                        itemCount={searchResult.length}
                        itemSize={getItemHeight}
                        width="100%"
                      >
                        {Row}
                      </VariableSizeList>
                    )}
                  </AutoSizer>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};

export const ExploreTab = withRequestAPI(_Explore);
