import { Store } from 'pullstate';
import { Instance, FileDIDDetails, RucioAuthCredentials, RucioAuthType } from '../types';

export interface UIState {
  activeInstance?: Instance;
  activeAuthType?: RucioAuthType;
  instances?: Instance[];
  authConfig?: { [instance: string]: RucioAuthCredentials };
  fileDetails: { [did: string]: FileDIDDetails };
  containerDetails: { [did: string]: FileDIDDetails[] };
}

export const initialState: UIState = {
  fileDetails: {},
  containerDetails: {}
};

export const UIStore = new Store(initialState);

export const resetRucioCaches = (): void => {
  UIStore.update(s => {
    s.fileDetails = {};
    s.containerDetails = {};
  });
};
