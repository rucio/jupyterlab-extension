import React from 'react';
import { useState } from 'react';
import renderer from 'react-test-renderer';
import { ExploreTab } from '../components/@Explore/ExploreTab';

it('empty Tab created', () => {

  const component = renderer.create(
    <ExploreTab />
  );
    
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot()
});