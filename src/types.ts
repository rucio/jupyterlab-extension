export interface Instance {
  displayName: string;
  name: string;
}

interface RucioAuth {
  account: string;
}

export interface RucioUserpassAuth extends RucioAuth {
  type: 'userpass';
  username: string;
  password: string;
}

export interface RucioX509Auth extends RucioAuth {
  type: 'x509';
  certificateFilePath: string;
  privateKeyFilePath: string;
}

export type RucioAuthCredentials = RucioUserpassAuth | RucioX509Auth;

export interface AttachedFile {
  did: string;
  size: number;
}

export interface FileDIDDetails {
  status: FileStatus;
  did: string;
  path?: string;
  size: number;
}

export interface NotebookDIDAttachment {
  did: string;
  variableName: string;
  type: 'container' | 'file';
}

export type FileStatus = 'OK' | 'REPLICATING' | 'NOT_AVAILABLE' | 'STUCK';
export type ContainerStatus = 'NOT_AVAILABLE' | 'AVAILABLE' | 'PARTIALLY_AVAILABLE' | 'REPLICATING' | 'STUCK';
