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
import { NotebookPanel } from '@jupyterlab/notebook';
import { NotebookDIDAttachment } from '../types';

export interface ExtensionState {
  activeNotebookPanel?: NotebookPanel;
  activeNotebookAttachment?: NotebookDIDAttachment[];
}

export const initialState: ExtensionState = {};

export const ExtensionStore = new Store(initialState);
