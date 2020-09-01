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
import { UIStore } from '../stores/UIStore';
import { actions } from './Actions';

export class PollingRequesterRef {}
type DIDType = 'file' | 'collection';
class DIDPollingManager {
  pollingRequesterMap: { [did: string]: { type: DIDType; refs: PollingRequesterRef[] } } = {};

  constructor() {
    setInterval(() => {
      this.poll();
    }, 10000);
  }

  requestPolling(did: string, type: DIDType, ref?: PollingRequesterRef, fetchNow = true) {
    if (!this.pollingRequesterMap[did]) {
      this.pollingRequesterMap[did] = { type, refs: [] };
    }

    const requesterRef = ref || new PollingRequesterRef();
    this.pollingRequesterMap[did].refs.push(requesterRef);

    if (fetchNow) {
      this.fetchDid(did);
    }

    return () => {
      this.disablePolling(did, requesterRef);
    };
  }

  disablePolling(did: string, ref: PollingRequesterRef) {
    if (this.pollingRequesterMap[did]) {
      this.pollingRequesterMap[did].refs = this.pollingRequesterMap[did].refs.filter(r => r !== ref);
    }
  }

  private poll() {
    const dids = Object.keys(this.pollingRequesterMap).filter(did => {
      return this.pollingRequesterMap[did] && this.pollingRequesterMap[did].refs.length > 0;
    });

    dids.forEach(did => {
      this.fetchDid(did);
    });
  }

  private fetchDid(did: string) {
    const { activeInstance } = UIStore.getRawState();

    if (!activeInstance) {
      return;
    }

    const type = this.pollingRequesterMap[did].type;
    switch (type) {
      case 'file':
        actions.getFileDIDDetails(activeInstance.name, did, true).then(details => {
          if (details.status !== 'REPLICATING') {
            delete this.pollingRequesterMap[did];
          }
        });
        break;
      case 'collection':
        actions.getCollectionDIDDetails(activeInstance.name, did, true).then(didDetails => {
          if (!didDetails.find(d => d.status === 'REPLICATING')) {
            delete this.pollingRequesterMap[did];
          }
        });
        break;
    }
  }
}

export const didPollingManager = new DIDPollingManager();

export interface WithPollingManagerProps {
  didPollingManager: DIDPollingManager;
}

//eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function withPollingManager<P>(Component: React.ComponentType<P>) {
  return class WithPollingManager extends React.Component<P> {
    //eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
    render() {
      const { ...props } = this.props;
      return <Component {...(props as P)} didPollingManager={didPollingManager} />;
    }
  };
}
