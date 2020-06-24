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
export async function requestAPI<T>(endPoint = '', init: RequestInit = {}, convertSnakeCase = true): Promise<T> {
  // Make request to Jupyter API
  const settings = ServerConnection.makeSettings();
  const requestUrl = URLExt.join(
    settings.baseUrl,
    EXTENSION_ID, // API Namespace
    endPoint
  );

  let response: Response;
  try {
    response = await ServerConnection.makeRequest(requestUrl, init, settings);
  } catch (error) {
    throw new ServerConnection.NetworkError(error);
  }

  const data = await response.json();

  if (!response.ok) {
    throw new ServerConnection.ResponseError(response, data.message);
  }

  return convertSnakeCase ? camelcaseKeysDeep(data) : data;
}
