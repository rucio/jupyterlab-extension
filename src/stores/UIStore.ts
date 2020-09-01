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

import { Store } from 'pullstate';
import { Instance, FileDIDDetails, RucioAuthCredentials, RucioAuthType } from '../types';

export interface UIState {
  activeInstance?: Instance;
  activeAuthType?: RucioAuthType;
  instances?: Instance[];
  authConfig?: { [instance: string]: RucioAuthCredentials };
  fileDetails: { [did: string]: FileDIDDetails };
  collectionDetails: { [did: string]: FileDIDDetails[] };
}

export const initialState: UIState = {
  fileDetails: {},
  collectionDetails: {}
};

export const UIStore = new Store(initialState);

export const resetRucioCaches = (): void => {
  UIStore.update(s => {
    s.fileDetails = {};
    s.collectionDetails = {};
  });
};
