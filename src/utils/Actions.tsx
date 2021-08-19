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

import React from 'react';
import qs from 'querystring';
import { requestAPI } from './ApiRequest';
import { UIStore } from '../stores/UIStore';
import {
  FileDIDDetails,
  AttachedFile,
  RucioAuthType,
  RucioAuthCredentials,
  InstanceConfig,
  DirectoryItem,
  DIDSearchType,
  DIDSearchResult
} from '../types';

export class Actions {
  async fetchInstancesConfig(): Promise<InstanceConfig> {
    return requestAPI<InstanceConfig>('instances');
  }

  async postActiveInstance(instanceName: string, authType: RucioAuthType): Promise<void> {
    const init = {
      method: 'PUT',
      body: JSON.stringify({
        instance: instanceName,
        auth: authType
      })
    };

    return requestAPI('instances', init);
  }

  async fetchAuthConfig<T extends any>(namespace: string, type: RucioAuthType): Promise<T> {
    const query = { namespace, type };
    return requestAPI<T>(`auth?${qs.encode(query)}`);
  }

  async putAuthConfig(namespace: string, type: RucioAuthType, params: RucioAuthCredentials): Promise<void> {
    const init = {
      method: 'PUT',
      body: JSON.stringify({
        namespace,
        type,
        params
      })
    };

    return requestAPI('auth', init);
  }

  async searchDID(namespace: string, did: string, type: DIDSearchType): Promise<DIDSearchResult[]> {
    const query = { namespace, did, type };
    return requestAPI<DIDSearchResult[]>(`did-search?${qs.encode(query)}`);
  }

  async fetchScopes(namespace: string): Promise<string[]> {
    const query = { namespace };
    return requestAPI<string[]>(`list-scopes?${qs.encode(query)}`);
  }

  async fetchAttachedFileDIDs(namespace: string, did: string): Promise<AttachedFile[]> {
    const query = { namespace, did };
    return requestAPI<AttachedFile[]>(`files?${qs.encode(query)}`);
  }

  async fetchDIDDetails(namespace: string, did: string, poll = false): Promise<FileDIDDetails[]> {
    const query = { namespace, did, poll: poll ? 1 : undefined };
    return requestAPI<FileDIDDetails[]>('did?' + qs.encode(query));
  }

  async getFileDIDDetails(namespace: string, did: string, poll = false): Promise<FileDIDDetails> {
    const fileDetails = UIStore.getRawState().fileDetails[did];

    if (!poll && !!fileDetails) {
      return fileDetails;
    }

    const didDetails = await this.fetchDIDDetails(namespace, did, poll);
    const didMap = didDetails.reduce((acc: { [did: string]: FileDIDDetails }, curr) => {
      acc[curr.did] = curr;
      return acc;
    }, {});

    UIStore.update(s => {
      s.fileDetails = { ...s.fileDetails, ...didMap };
    });

    return didDetails[0];
  }

  async getCollectionDIDDetails(namespace: string, did: string, poll = false): Promise<FileDIDDetails[]> {
    const collectionDetails = UIStore.getRawState().collectionDetails[did];
    if (!poll && !!collectionDetails) {
      return collectionDetails;
    }

    const didDetails = await this.fetchDIDDetails(namespace, did, poll);

    UIStore.update(s => {
      s.collectionDetails[did] = didDetails;
    });

    return didDetails;
  }

  async makeFileAvailable(namespace: string, did: string): Promise<void> {
    const fileDetails = UIStore.getRawState().fileDetails[did];
    UIStore.update(s => {
      s.fileDetails[did] = { ...fileDetails, status: 'REPLICATING' };
    });

    const init = {
      method: 'POST',
      body: JSON.stringify({ did })
    };

    return requestAPI('did/make-available?namespace=' + encodeURIComponent(namespace), init);
  }

  async makeCollectionAvailable(namespace: string, did: string): Promise<void> {
    const collectionAttachedFiles = UIStore.getRawState().collectionDetails[did];
    const updatedCollectionAttachedFiles: FileDIDDetails[] = collectionAttachedFiles.map(f => ({
      ...f,
      status: f.status === 'OK' ? 'OK' : 'REPLICATING'
    }));
    UIStore.update(s => {
      s.collectionDetails[did] = updatedCollectionAttachedFiles;
    });

    const init = {
      method: 'POST',
      body: JSON.stringify({ did })
    };

    return requestAPI('did/make-available?namespace=' + encodeURIComponent(namespace), init);
  }

  async listDirectory(path: string): Promise<DirectoryItem[]> {
    return requestAPI<DirectoryItem[]>('file-browser?path=' + encodeURIComponent(path));
  }

  async purgeCache(): Promise<void> {
    const init = {
      method: 'POST'
    };

    return requestAPI('purge-cache', init);
  }
}

export const actions = new Actions();

export interface WithRequestAPIProps {
  actions: Actions;
}

//eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function withRequestAPI<P>(Component: React.ComponentType<P>) {
  return class WithRequestAPI extends React.Component<P> {
    //eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
    render() {
      const { ...props } = this.props;
      return <Component {...(props as P)} actions={actions} />;
    }
  };
}
