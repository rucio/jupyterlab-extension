export interface Instance {
  displayName: string;
  name: string;
}

export interface FileDIDDetails {
  status: 'OK' | 'REPLICATING' | 'NOT_AVAILABLE' | 'STUCK';
  path?: string;
}
