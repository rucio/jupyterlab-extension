import React from 'react';
import { useState } from 'react';
import renderer from 'react-test-renderer';
import {
  MetadataFilterItem,
  IMetadataFilter
} from '../components/@Explore/MetadataFilterItem';

import {
  MetadataFilterContainer,
  IMetadataFilterContainer
} from '../components/@Explore/MetadataFilterContainer';


it('empty filter created', () => {

  const emptyFilter: IMetadataFilter = {
    logic: 'And',
    key: '',
    operator: '=',
    value: ''
  };

  const component = renderer.create(
    <MetadataFilterItem
      filter={emptyFilter}
      showBoolOperatorDropdown={true}
      onDelete={() => {}}
      onChange={() => {}}
      onKeyPress={() => {}}
    />
  );
    
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot()
});


it('empty filter container created', () => {

  const realUseState = jest.fn();

  var initialFilters = [] as IMetadataFilter[];
  //jest
  //  .spyOn(React, 'useState')
  //  .mockImplementationOnce(() => [initialFilters, () => null])

  const component = renderer.create(
    <MetadataFilterContainer
      onKeyPress={() => null}
      metadataFilters={initialFilters}
      setMetadataFilters={ () => null}
    />
  );
    
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot()
});

it('one filter container created', () => {

  const realUseState = jest.fn();

  var initialFilters = [{ logic: 'And', key: '', operator: '=', value: '' }] as IMetadataFilter[];
  //jest
  //  .spyOn(React, 'useState')
  //  .mockImplementationOnce(() => [initialFilters, () => null])

  const component = renderer.create(
    <MetadataFilterContainer
      onKeyPress={() => null}
      metadataFilters={initialFilters}
      setMetadataFilters={ () => null}
    />
  );
    
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot()
});
