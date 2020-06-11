import { Store } from 'pullstate';
import { NotebookPanel } from '@jupyterlab/notebook';
import { NotebookDIDAttachment } from '../types';

export interface ExtensionState {
  activeNotebookPanel?: NotebookPanel;
  activeNotebookAttachment?: NotebookDIDAttachment[];
}

export const initialState: ExtensionState = {};

export const ExtensionStore = new Store(initialState);
