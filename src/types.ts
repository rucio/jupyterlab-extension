/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
 */

export interface Instance {
  displayName: string;
  name: string;
  mode: 'replica' | 'download';
  oidcEnabled: boolean;
  webuiUrl?: string;
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

export interface RucioX509ProxyAuth extends RucioAuth {
  proxy: string;
}

export type RucioAuthCredentials = RucioUserpassAuth | RucioX509Auth | RucioX509ProxyAuth;

export type RucioAuthType = 'userpass' | 'x509' | 'x509_proxy' | 'oidc';

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
  pfn?: string;
  size: number;
}

export interface NotebookDIDAttachment {
  did: string;
  variableName: string;
  type: 'collection' | 'file';
}

export interface DirectoryItem {
  type: 'file' | 'dir';
  name: string;
  path: string;
}

export type FileStatus = 'OK' | 'REPLICATING' | 'NOT_AVAILABLE' | 'STUCK';
export type CollectionStatus = 'NOT_AVAILABLE' | 'AVAILABLE' | 'PARTIALLY_AVAILABLE' | 'REPLICATING' | 'STUCK' | 'EMPTY';
export type ResolveStatus = 'NOT_RESOLVED' | 'RESOLVING' | 'PENDING_INJECTION' | 'READY' | 'FAILED';

export type DIDSearchType = 'collection' | 'dataset' | 'container' | 'file' | 'all';

export interface DIDSearchResult {
  did: string;
  type: 'dataset' | 'container' | 'file';
  size?: number;
}
