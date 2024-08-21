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

import { requestAPI } from '../utils/ApiRequest';

jest.mock('@jupyterlab/services', () => ({
    ServerConnection: {
        makeSettings: () => ({ baseUrl: 'http://localhost:8888/' }),
        makeRequest: () => ({
            ok: true,
            json: () => ({ request_body_1: 'hello', request_body_2: 'world' })
        })
    }
}));

describe('requestAPI', () => {
    test('request OK should convert to camel case', async () => {
        const response = await requestAPI<any>('/resource1');
        expect(response).toEqual({ requestBody1: 'hello', requestBody2: 'world' });
    })

    test('request OK should NOT convert to camel case', async () => {
        const response = await requestAPI<any>('/resource1', {}, false);
        expect(response).toEqual({ request_body_1: 'hello', request_body_2: 'world' });
    })
})

