import { Store } from 'pullstate';
import { NotebookPanel } from '@jupyterlab/notebook';

export interface ExtensionState {
  activeNotebookPanel?: NotebookPanel;
}

export const initialState: ExtensionState = {};

export const ExtensionStore = new Store(initialState);
