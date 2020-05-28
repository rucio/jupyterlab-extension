import { Store } from 'pullstate';
import { Instance } from './types';

export interface State {
  activeInstance?: Instance;
  activeMenu: any;
}

export const initialState: State = {
  activeMenu: 1
};

export const ExtensionStore = new Store(initialState);
