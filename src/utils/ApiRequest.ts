/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020
 * - Enrique Garcia, (CERN), 2024
 */

import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import camelcaseKeysDeep from 'camelcase-keys-deep';
import { EXTENSION_ID } from '../const';

/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
export async function requestAPI<T>(
  endPoint = '',
  init: RequestInit = {},
  convertSnakeCase = true
): Promise<T> {
  const settings = ServerConnection.makeSettings();
  const [path, queryString] = endPoint.split('?');
  const base = URLExt.join(settings.baseUrl, EXTENSION_ID, path);
  const requestUrl = queryString ? `${base}?${queryString}` : base;

  let response: Response;
  try {
    response = await ServerConnection.makeRequest(requestUrl, init, settings);
  } catch (error) {
    throw new ServerConnection.NetworkError(error as TypeError);
  }

  const data = await response.json();

  if (!response.ok) {
    const error = new ServerConnection.ResponseError(response, data.message);
    (error as any).exception_class = data.exception_class;
    (error as any).exception_message = data.exception_message;
    (error as any).error = data.error; // Optional
    throw error;
  }

  return convertSnakeCase ? camelcaseKeysDeep(data) : data;
}
