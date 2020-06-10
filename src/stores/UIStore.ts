import { Store } from 'pullstate';
import { Instance, FileDIDDetails } from '../types';

export interface UIState {
  activeInstance?: Instance;
  fileDetails: { [did: string]: FileDIDDetails };
  containerDetails: { [did: string]: FileDIDDetails[] };
}

export const initialState: UIState = {
  fileDetails: {},
  containerDetails: {}
};

export const UIStore = new Store(initialState);
