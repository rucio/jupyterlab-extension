import React from 'react';
import renderer from 'react-test-renderer';
import { MetadataFilterItem, IMetadataFilter } from '../components/@Explore/MetadataFilterItem';

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