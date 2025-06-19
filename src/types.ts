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

export interface IInstance {
  displayName: string;
  name: string;
  mode: 'replica' | 'download';
  oidcEnabled: boolean;
  webuiUrl?: string;
}

interface IRucioAuth {
  account?: string;
}

export interface IRucioOIDCAuth extends IRucioAuth {}

export interface IRucioUserpassAuth extends IRucioAuth {
  username: string;
  password: string;
}

export interface IRucioX509Auth extends IRucioAuth {
  certificate: string;
  key?: string;
}

export interface IRucioX509ProxyAuth extends IRucioAuth {
  proxy: string;
}

export type RucioAuthCredentials =
  | IRucioUserpassAuth
  | IRucioX509Auth
  | IRucioX509ProxyAuth
  | IRucioOIDCAuth;

export type RucioAuthType = 'userpass' | 'x509' | 'x509_proxy' | 'oidc';

export interface IInstanceConfig {
  activeInstance?: string;
  instances: IInstance[];
  authType?: RucioAuthType;
}

export interface IAttachedFile {
  did: string;
  size: number;
}

export interface IFetchScopesResult {
  success: boolean;
  scopes: string[];
  error?: string; // Optional property for error messages
}

export interface IFileDIDDetails {
  status: FileStatus;
  did: string;
  path?: string;
  pfn?: string;
  size: number;
  error?: string;
}

export interface INotebookDIDAttachment {
  did: string;
  variableName: string;
  type: 'collection' | 'file';
}

export interface IDirectoryItem {
  type: 'file' | 'dir';
  name: string;
  path: string;
}

export type FileStatus =
  | 'OK'
  | 'REPLICATING'
  | 'NOT_AVAILABLE'
  | 'STUCK'
  | 'FAILED';
export type CollectionStatus =
  | 'NOT_AVAILABLE'
  | 'AVAILABLE'
  | 'PARTIALLY_AVAILABLE'
  | 'REPLICATING'
  | 'STUCK'
  | 'EMPTY';
export type ResolveStatus =
  | 'NOT_RESOLVED'
  | 'RESOLVING'
  | 'PENDING_INJECTION'
  | 'READY'
  | 'FAILED';

export type DIDSearchType =
  | 'collection'
  | 'dataset'
  | 'container'
  | 'file'
  | 'all';

export interface IDIDSearchResult {
  did: string;
  type: 'dataset' | 'container' | 'file';
  size?: number;
}

export type FileUploadParam = {
  paths: string[];
  rse: string;
  fileScope: string;
  addToDataset?: boolean;
  datasetScope?: string;
  datasetName?: string;
  lifetime?: number;
};

export type FileUploadStatus = 'OK' | 'FAILED' | 'UPLOADING';

export type FileUploadJob = {
  id: string;
  did: string;
  datasetDid?: string;
  path: string;
  rse: string;
  uploaded: boolean;
  lifetime?: number;
  pid: number;
  status: FileUploadStatus;
};

export type FileUploadLog = {
  text: string;
};
