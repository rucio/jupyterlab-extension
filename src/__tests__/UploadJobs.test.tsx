/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 */

import React from 'react';
import renderer, { ReactTestInstance } from 'react-test-renderer';
import { ServerConnection } from '@jupyterlab/services';
import { actions } from '../utils/Actions';
import { UploadJobListItem } from '../components/@Uploads/UploadJobListItem';

jest.mock('@jupyterlab/services', () => ({
  ServerConnection: {
    makeSettings: () => ({ baseUrl: 'http://localhost:8888/' }),
    makeRequest: jest.fn()
  }
}));
jest.mock('../widgets/UploadLogViewerWidget', () => ({
  UploadLogViewerWidget: jest.fn()
}));

const backendJobs = [
  {
    id: 1,
    namespace: 'atlas',
    did: 'user.test:file_a.txt',
    dataset_did: 'user.test:my_dataset',
    path: 'data/file_a.txt',
    rse: 'MOCK_RSE',
    uploaded: true,
    lifetime: null,
    pid: 1234,
    status: 'OK'
  },
  {
    id: 2,
    namespace: 'atlas',
    did: 'user.test:file_b.txt',
    dataset_did: null,
    path: 'data/file_b.txt',
    rse: 'MOCK_RSE',
    uploaded: true,
    lifetime: null,
    pid: 1235,
    status: 'OK'
  }
];

const textOf = (root: ReactTestInstance): string[] =>
  root
    .findAllByType('div')
    .map(div =>
      div.children.filter(child => typeof child === 'string').join('')
    );

describe('upload jobs dataset DID', () => {
  beforeEach(() => {
    const makeRequest = ServerConnection.makeRequest as jest.Mock;
    makeRequest.mockReset();
    makeRequest.mockResolvedValue({
      ok: true,
      json: async () => backendJobs
    });
  });

  test('fetchUploadJobs converts backend dataset_did to datasetDid', async () => {
    const jobs = await actions.fetchUploadJobs('atlas');

    expect(ServerConnection.makeRequest).toBeCalledWith(
      expect.stringContaining('upload/jobs?namespace=atlas'),
      {},
      expect.anything()
    );
    expect(jobs[0].datasetDid).toBe('user.test:my_dataset');
    expect(jobs[0]).not.toHaveProperty('dataset_did');
    expect(jobs[1].datasetDid).toBeNull();
  });

  test('upload job list item shows the dataset only for dataset uploads', async () => {
    const [datasetJob, fileOnlyJob] = await actions.fetchUploadJobs('atlas');

    const datasetItem = renderer.create(<UploadJobListItem job={datasetJob} />);
    expect(textOf(datasetItem.root)).toContain('Dataset: user.test:my_dataset');

    const fileOnlyItem = renderer.create(<UploadJobListItem job={fileOnlyJob} />);
    expect(
      textOf(fileOnlyItem.root).some(text => text.startsWith('Dataset:'))
    ).toBe(false);
  });
});
