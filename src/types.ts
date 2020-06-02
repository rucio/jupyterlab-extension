export interface Instance {
  displayName: string;
  name: string;
}

export interface FileDIDDetails {
  status: 'available' | 'replicating' | 'unavailable';
  path?: string;
}
