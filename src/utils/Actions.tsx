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
  IFileDIDDetails,
  IAttachedFile,
  RucioAuthType,
  RucioAuthCredentials,
  IInstanceConfig,
  IFetchScopesResult,
  IDirectoryItem,
  DIDSearchType,
  IDIDSearchResult,
  FileUploadParam,
  FileUploadJob,
  FileUploadLog
} from '../types';

export type AuthConfigResponse = {
  success: boolean;
  lifetime?: string;
  error?: string;
  exception_class?: string;
  exception_message?: string;
};

export class Actions {
  async fetchInstancesConfig(): Promise<IInstanceConfig> {
    return requestAPI<IInstanceConfig>('instances');
  }

  async postActiveInstance(
    instanceName: string,
    authType: RucioAuthType
  ): Promise<void> {
    const init = {
      method: 'PUT',
      body: JSON.stringify({
        instance: instanceName,
        auth: authType
      })
    };

    return requestAPI('instances', init);
  }

  async fetchAuthConfig<T>(namespace: string, type: RucioAuthType): Promise<T> {
    const query = { namespace, type };
    const encodedQuery = qs.encode(query);

    const response = await requestAPI<T>(`auth?${encodedQuery}`);
    return response;
  }

  async putAuthConfig(
    namespace: string,
    type: RucioAuthType,
    params: RucioAuthCredentials
  ): Promise<AuthConfigResponse> {
    const init = {
      method: 'PUT',
      body: JSON.stringify({
        namespace,
        type,
        params
      })
    };

    return requestAPI<AuthConfigResponse>('auth', init);
  }

  async searchDID(
    namespace: string,
    did: string,
    type: DIDSearchType,
    filters: string
  ): Promise<IDIDSearchResult[]> {
    const query = { namespace, did, type, filters };
    return requestAPI<IDIDSearchResult[]>(`did-search?${qs.encode(query)}`);
  }

  async fetchScopes(namespace: string): Promise<IFetchScopesResult> {
    const query = { namespace };
    return requestAPI<IFetchScopesResult>(`list-scopes?${qs.encode(query)}`);
  }

  async fetchRSEs(namespace: string, expression?: string): Promise<string[]> {
    const query = { namespace, expression };
    return requestAPI<string[]>(`list-rses?${qs.encode(query)}`);
  }

  async fetchAttachedFileDIDs(
    namespace: string,
    did: string
  ): Promise<IAttachedFile[]> {
    const query = { namespace, did };
    return requestAPI<IAttachedFile[]>(`files?${qs.encode(query)}`);
  }

  async fetchDIDDetails(
    namespace: string,
    did: string,
    poll = false
  ): Promise<IFileDIDDetails[]> {
    const query = { namespace, did, poll: poll ? 1 : undefined };
    return requestAPI<IFileDIDDetails[]>('did?' + qs.encode(query));
  }

  async getFileDIDDetails(
    namespace: string,
    did: string,
    poll = false
  ): Promise<IFileDIDDetails> {
    const fileDetails = UIStore.getRawState().fileDetails[did];

    if (!poll && !!fileDetails) {
      return fileDetails;
    }

    const didDetails = await this.fetchDIDDetails(namespace, did, poll);
    const didMap = didDetails.reduce(
      (acc: { [did: string]: IFileDIDDetails }, curr) => {
        acc[curr.did] = curr;
        return acc;
      },
      {}
    );

    UIStore.update(s => {
      s.fileDetails = { ...s.fileDetails, ...didMap };
    });

    return didDetails[0];
  }

  async getCollectionDIDDetails(
    namespace: string,
    did: string,
    poll = false
  ): Promise<IFileDIDDetails[]> {
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

    return requestAPI(
      'did/make-available?namespace=' + encodeURIComponent(namespace),
      init
    );
  }

  async makeCollectionAvailable(namespace: string, did: string): Promise<void> {
    const collectionAttachedFiles =
      UIStore.getRawState().collectionDetails[did];
    const updatedCollectionAttachedFiles: IFileDIDDetails[] =
      collectionAttachedFiles.map(f => ({
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

    return requestAPI(
      'did/make-available?namespace=' + encodeURIComponent(namespace),
      init
    );
  }

  async listDirectory(path: string): Promise<IDirectoryItem[]> {
    return requestAPI<IDirectoryItem[]>(
      'file-browser?path=' + encodeURIComponent(path)
    );
  }

  async purgeCache(): Promise<void> {
    const init = {
      method: 'POST'
    };

    return requestAPI('purge-cache', init);
  }

  async uploadFile(namespace: string, params: FileUploadParam): Promise<void> {
    const {
      paths,
      rse,
      fileScope,
      datasetName,
      addToDataset,
      datasetScope,
      lifetime
    } = params;

    const init = {
      method: 'POST',
      body: JSON.stringify({
        file_paths: paths,
        rse,
        scope: fileScope,
        add_to_dataset: !!addToDataset,
        dataset_scope: datasetScope,
        dataset_name: datasetName,
        lifetime
      })
    };

    return requestAPI(
      'upload?namespace=' + encodeURIComponent(namespace),
      init
    );
  }

  async fetchUploadJobs(namespace: string): Promise<FileUploadJob[]> {
    const query = { namespace };
    return requestAPI<FileUploadJob[]>('upload/jobs?' + qs.encode(query));
  }

  async fetchUploadJobLog(
    namespace: string,
    id: string
  ): Promise<FileUploadLog> {
    const query = { namespace, id };
    return requestAPI<FileUploadLog>('upload/jobs/log?' + qs.encode(query));
  }

  async deleteUploadJob(namespace: string, id: string): Promise<void> {
    const query = { namespace, id };
    const init = {
      method: 'DELETE'
    };
    return requestAPI<void>('upload/jobs/details?' + qs.encode(query), init);
  }
}

export const actions = new Actions();

export interface IWithRequestAPIProps {
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
