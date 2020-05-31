export interface Instance {
  displayName: string;
  value: string;
}

export interface FileDIDDetails {
  status: 'available' | 'replicating' | 'unavailable';
  path?: string;
}
