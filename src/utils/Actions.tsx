import React from 'react';
import qs from 'querystring';
import { requestAPI } from './ApiRequest';
import { UIStore } from '../stores/UIStore';
import { FileDIDDetails, Instance, AttachedFile, RucioAuthType, RucioAuthCredentials } from '../types';

export class Actions {
  async fetchInstancesConfig(): Promise<{
    activeInstance?: string;
    authType?: RucioAuthType;
    instances: Instance[];
  }> {
    return requestAPI<{ activeInstance?: string; authType?: RucioAuthType; instances: Instance[] }>('instances');
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

  async getAuthConfig<T extends any>(namespace: string, type: RucioAuthType): Promise<T> {
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

  async getContainerDIDDetails(namespace: string, did: string, poll = false): Promise<FileDIDDetails[]> {
    const containerDetails = UIStore.getRawState().containerDetails[did];
    if (!poll && !!containerDetails) {
      return containerDetails;
    }

    const didDetails = await this.fetchDIDDetails(namespace, did, poll);
    const fileDIDMap = didDetails
      .filter(d => d.status === 'OK')
      .reduce((acc: { [did: string]: FileDIDDetails }, curr) => {
        acc[curr.did] = curr;
        return acc;
      }, {});

    UIStore.update(s => {
      s.containerDetails[did] = didDetails;
      s.fileDetails = { ...s.fileDetails, ...fileDIDMap };
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
      body: JSON.stringify({ method: 'replica', did })
    };

    return requestAPI('did/make-available?namespace=' + encodeURIComponent(namespace), init);
  }

  async makeContainerAvailable(namespace: string, did: string): Promise<void> {
    const containerAttachedFiles = UIStore.getRawState().containerDetails[did];
    const updatedContainerAttachedFiles: FileDIDDetails[] = containerAttachedFiles.map(f => ({
      ...f,
      status: f.status === 'OK' ? 'OK' : 'REPLICATING'
    }));
    UIStore.update(s => {
      s.containerDetails[did] = updatedContainerAttachedFiles;
    });

    const init = {
      method: 'POST',
      body: JSON.stringify({ method: 'replica', did })
    };

    return requestAPI('did/make-available?namespace=' + encodeURIComponent(namespace), init);
  }
}

export interface WithRequestAPIProps {
  actions: Actions;
}

//eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function withRequestAPI<P>(Component: React.ComponentType<P>) {
  return class WithRequestAPI extends React.Component<P> {
    actions = new Actions();

    //eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
    render() {
      const { ...props } = this.props;
      return <Component {...(props as P)} actions={this.actions} />;
    }
  };
}
