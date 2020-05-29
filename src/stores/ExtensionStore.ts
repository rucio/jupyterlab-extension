import { Store } from 'pullstate';
import { Instance } from '../types';

export interface State {
  activeInstance?: Instance;
  activeMenu: any;
  searchBy: string;
}

export const initialState: State = {
  activeMenu: 1,
  searchBy: 'datasets'
};

export const ExtensionStore = new Store(initialState);
