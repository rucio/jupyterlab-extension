export interface Instance {
  displayName: string;
  name: string;
}

export interface FileDIDDetails {
  status: FileStatus;
  did: string;
  path?: string;
}

export interface NotebookDIDAttachment {
  did: string;
  variableName: string;
  type: 'container' | 'file';
}

export type FileStatus = 'OK' | 'REPLICATING' | 'NOT_AVAILABLE' | 'STUCK';
export type ContainerStatus =
  | 'NOT_AVAILABLE'
  | 'AVAILABLE'
  | 'PARTIALLY_AVAILABLE'
  | 'REPLICATING'
  | 'STUCK';
