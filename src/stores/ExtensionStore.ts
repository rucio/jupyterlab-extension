import { Store } from 'pullstate';
import { Instance, FileDIDDetails } from '../types';

export interface State {
  activeInstance?: Instance;
  fileDetails: { [did: string]: FileDIDDetails };
}

export const initialState: State = {
  fileDetails: {}
};

export const ExtensionStore = new Store(initialState);
