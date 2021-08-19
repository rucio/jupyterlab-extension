/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
 */

import React, { useState, useEffect, useRef } from 'react';
import { createUseStyles } from 'react-jss';
import { VariableSizeList } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import { useStoreState } from 'pullstate';
import { UIStore } from '../stores/UIStore';
import { TextField } from '../components/TextField';
import { HorizontalHeading } from '../components/HorizontalHeading';
import { DIDListItem } from '../components/@Explore/DIDListItem';
import { Spinning } from '../components/Spinning';
import { withRequestAPI, WithRequestAPIProps } from '../utils/Actions';
import { DIDSearchType, DIDSearchResult } from '../types';
import { InlineDropdown } from '../components/@Explore/InlineDropdown';
import { ListScopesPopover } from '../components/@Explore/ListScopesPopover';

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

  const { actions } = props as WithRequestAPIProps;

  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<DIDSearchType>('all');
  const [searchResult, setSearchResult] = useState<DIDSearchResult[]>();
  const [didExpanded, setDidExpanded] = useState<{ [index: number]: boolean }>({});
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

    return 1;
  };

  useEffect(() => {
    if (!lastQuery || !activeInstance) {
      return;
    }

    setLoading(true);
    setSearchResult(undefined);
    setDidExpanded({});
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
          setError('Wildcard search is disabled.');
        }
      })
      .finally(() => setLoading(false));
  }, [lastQuery, searchType]);

  const searchBoxRef = useRef<any>(null);
  const onScopeClicked = (scope: string) => {
    setSearchQuery(scope + ':');
    searchBoxRef?.current?.focus();
  };

  const listScopesButton = (
    <ListScopesPopover onScopeClicked={onScopeClicked}>
      <div className={classes.listScopesButton}>
        <i className={`${classes.listScopesIcon} material-icons`}>topic</i>
      </div>
    </ListScopesPopover>
  );

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
      {loading && (
        <div className={classes.loading}>
          <Spinning className={`${classes.icon} material-icons`}>hourglass_top</Spinning>
          <span className={classes.iconText}>Loading...</span>
        </div>
      )}
      {!!searchResult && (
        <>
          <HorizontalHeading title="Search Results" />
          {((!!searchResult && searchResult.length === 0) || !!error) && (
            <div className={classes.loading}>{error || 'No results found'}</div>
          )}
          <div className={classes.resultsContainer}>
            <AutoSizer disableWidth>
              {({ height }) => (
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
        </>
      )}
    </div>
  );
};

export const Explore = withRequestAPI(_Explore);
