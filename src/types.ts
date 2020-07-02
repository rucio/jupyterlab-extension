export interface Instance {
  displayName: string;
  name: string;
}

interface RucioAuth {
  account?: string;
}

export interface RucioUserpassAuth extends RucioAuth {
  username: string;
  password: string;
}

export interface RucioX509Auth extends RucioAuth {
  certificate: string;
  key?: string;
}

export type RucioAuthCredentials = RucioUserpassAuth | RucioX509Auth;

export type RucioAuthType = 'userpass' | 'x509';

export interface InstanceConfig {
  activeInstance?: string;
  instances: Instance[];
  authType?: RucioAuthType;
}

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
export type ResolveStatus = 'NOT_RESOLVED' | 'RESOLVING' | 'PENDING_INJECTION' | 'READY' | 'FAILED';
