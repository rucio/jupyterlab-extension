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

export const EXTENSION_ID = 'rucio-jupyterlab';
export const METADATA_ATTACHMENTS_KEY = 'rucio_attachments';
export const COMM_NAME_KERNEL = `${EXTENSION_ID}:kernel`;
export const COMM_NAME_FRONTEND = `${EXTENSION_ID}:frontend`;

export const searchByOptions = [
  { title: 'Datasets or Containers', value: 'datasets' },
  { title: 'Files', value: 'files' }
];
