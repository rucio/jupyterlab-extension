import { Store } from 'pullstate';
import { Instance } from '../types';

export interface State {
  activeInstance?: Instance;
}

export const initialState: State = {};

export const ExtensionStore = new Store(initialState);
