/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021
 */

import { computeCollectionState, toHumanReadableSize, checkVariableNameValid } from '../utils/Helpers';
import { IFileDIDDetails } from '../types';

describe('toHumanReadableSize', () => {
    test('return bytes value', () => {
        const humanReadableValue = toHumanReadableSize(123);
        expect(humanReadableValue).toBe('123B');
    })
    
    test('return kibibytes value', () => {
        const humanReadableValue = toHumanReadableSize(123 * 1024);
        expect(humanReadableValue).toBe('123KiB');
    })
    
    test('return mebibytes value', () => {
        const humanReadableValue = toHumanReadableSize(123 * 1024 * 1024);
        expect(humanReadableValue).toBe('123MiB');
    })
    
    test('return gibibytes value', () => {
        const humanReadableValue = toHumanReadableSize(123 * 1024 * 1024 * 1024);
        expect(humanReadableValue).toBe('123GiB');
    })
})

describe('computeCollectionState', () => {
    test('empty files should return EMPTY', () => {
        const mockFiles: IFileDIDDetails[] = [];
    
        const computedState = computeCollectionState(mockFiles);
        expect(computedState).toBe('EMPTY');
    })
    
    test('null files should return false', () => {
        const mockFiles: IFileDIDDetails[] | undefined = undefined;
    
        const computedState = computeCollectionState(mockFiles);
        expect(computedState).toBeFalsy();
    })
    
    test('all available should return AVAILABLE', () => {
        const mockFiles: IFileDIDDetails[] = [
            { status: 'OK', did: 'scope:name1', path: '/eos/rucio/1231', size: 123 },
            { status: 'OK', did: 'scope:name2', path: '/eos/rucio/1232', size: 123 },
            { status: 'OK', did: 'scope:name3', path: '/eos/rucio/1233', size: 123 }
        ];
    
        const computedState = computeCollectionState(mockFiles);
        expect(computedState).toBe('AVAILABLE');
    })
    
    test('some available should return PARTIALLY_AVAILABLE', () => {
        const mockFiles: IFileDIDDetails[] = [
            { status: 'NOT_AVAILABLE', did: 'scope:name1', path: '/eos/rucio/1231', size: 123 },
            { status: 'OK', did: 'scope:name2', path: '/eos/rucio/1232', size: 123 },
            { status: 'OK', did: 'scope:name3', path: '/eos/rucio/1233', size: 123 }
        ];
    
        const computedState = computeCollectionState(mockFiles);
        expect(computedState).toBe('PARTIALLY_AVAILABLE');
    })
    
    test('some replicating should return REPLICATING', () => {
        const mockFiles: IFileDIDDetails[] = [
            { status: 'NOT_AVAILABLE', did: 'scope:name1', path: '/eos/rucio/1231', size: 123 },
            { status: 'REPLICATING', did: 'scope:name2', path: '/eos/rucio/1232', size: 123 },
            { status: 'OK', did: 'scope:name3', path: '/eos/rucio/1233', size: 123 }
        ];
    
        const computedState = computeCollectionState(mockFiles);
        expect(computedState).toBe('REPLICATING');
    })

    test('fetching should return FETCHING before other states', () => {
        const mockFiles: IFileDIDDetails[] = [
            { status: 'FETCHING', did: 'scope:name1', path: undefined, size: 0 },
            { status: 'REPLICATING', did: 'scope:name2', path: '/eos/rucio/1232', size: 123 },
            { status: 'OK', did: 'scope:name3', path: '/eos/rucio/1233', size: 123 }
        ];

        const computedState = computeCollectionState(mockFiles);
        expect(computedState).toBe('FETCHING');
    })
    
    test('some stuck should return STUCK', () => {
        const mockFiles: IFileDIDDetails[] = [
            { status: 'OK', did: 'scope:name1', path: '/eos/rucio/1231', size: 123 },
            { status: 'STUCK', did: 'scope:name2', path: '/eos/rucio/1232', size: 123 },
            { status: 'OK', did: 'scope:name3', path: '/eos/rucio/1233', size: 123 }
        ];
    
        const computedState = computeCollectionState(mockFiles);
        expect(computedState).toBe('STUCK');
    })
    
    test('none available should return NOT_AVAILABLE', () => {
        const mockFiles: IFileDIDDetails[] = [
            { status: 'NOT_AVAILABLE', did: 'scope:name1', path: '/eos/rucio/1231', size: 123 },
            { status: 'NOT_AVAILABLE', did: 'scope:name2', path: '/eos/rucio/1232', size: 123 },
            { status: 'NOT_AVAILABLE', did: 'scope:name3', path: '/eos/rucio/1233', size: 123 }
        ];
    
        const computedState = computeCollectionState(mockFiles);
        expect(computedState).toBe('NOT_AVAILABLE');
    })
})

describe('checkVariableNameValid', () => {
    test('all letters should return true', () => {
        expect(checkVariableNameValid('myVariable')).toBeTruthy();
    })
    
    test('letters with underscores should return true', () => {
        expect(checkVariableNameValid('my_variable')).toBeTruthy();
    })
    
    test('letters with numbers should return true', () => {
        expect(checkVariableNameValid('my2variable123')).toBeTruthy();
    })
    
    test('begins with number should return false', () => {
        expect(checkVariableNameValid('2variable')).toBeFalsy();
    })
    
    test('with special characters other than underscore should return false', () => {
        expect(checkVariableNameValid('my-variable')).toBeFalsy();
    })
    
    test('with space should return false', () => {
        expect(checkVariableNameValid('my variable')).toBeFalsy();
    })
    
    test('empty should return false', () => {
        expect(checkVariableNameValid('')).toBeFalsy();
    })
})