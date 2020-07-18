jest.mock('../src/utils/ApiRequest');
jest.mock('../src/stores/UIStore');

import { requestAPI } from '../src/utils/ApiRequest';
import { Actions } from '../src/utils/Actions';
import { Instance, AttachedFile, FileDIDDetails, RucioAuthCredentials } from '../src/types';
import { UIStore } from '../src/stores/UIStore';

describe('fetchInstancesConfig', () => {
    test('should call /instances endpoint', async () => {
        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        const mockInstanceConfig = {
            activeInstance: 'atlas',
            instances: [] as Instance[]
        };

        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve(mockInstanceConfig));

        const actions = new Actions();
        const instancesConfig = await actions.fetchInstancesConfig();

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringContaining('instances')
        )

        expect(instancesConfig).toEqual(mockInstanceConfig)
    })
})

describe('postActiveInstance', () => {
    test('should call /instances endpoint with method PUT', async () => {
        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;

        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve());

        const actions = new Actions();
        await actions.postActiveInstance('atlas', 'userpass');

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringContaining('instances'),
            expect.objectContaining({
                method: 'PUT',
                body: JSON.stringify({
                    instance: 'atlas',
                    auth: 'userpass'
                })
            })
        )
    })
})

describe('fetchAuthConfig', () => {
    test('should call /auth endpoint with query', async () => {
        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        const mockAuthConfig: RucioAuthCredentials = {
            username: 'username',
            password: 'password',
            account: 'account'
        }

        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve(mockAuthConfig));

        const actions = new Actions();
        const attachedDIDs = await actions.fetchAuthConfig('atlas', 'userpass');

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringMatching(/(\b(auth|type=userpass|namespace=atlas)\b.*){3,}/)
        )

        expect(attachedDIDs).toEqual(mockAuthConfig);
    })
})

describe('putAuthConfig', () => {
    test('should call /auth endpoint with method PUT', async () => {
        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        const mockAuthConfig: RucioAuthCredentials = {
            username: 'username',
            password: 'password',
            account: 'account'
        }

        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve());

        const actions = new Actions();
        await actions.putAuthConfig('atlas', 'userpass', mockAuthConfig);

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringContaining('auth'),
            expect.objectContaining({
                method: 'PUT',
                body: JSON.stringify({
                    namespace: 'atlas',
                    type: 'userpass',
                    params: mockAuthConfig
                })
            })
        )
    })
})


describe('fetchAttachedFileDIDs', () => {
    test('should call /files endpoint with query', async () => {
        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        const mockAttachedFiles: AttachedFile[] = [
            { did: 'scope:name1', size: 123 },
            { did: 'scope:name2', size: 123 },
            { did: 'scope:name3', size: 123 }
        ]

        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve(mockAttachedFiles));

        const actions = new Actions();
        const attachedDIDs = await actions.fetchAttachedFileDIDs('atlas', 'scope:name');

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringMatching(/(\b(files|did=scope%3Aname|namespace=atlas)\b.*){3,}/)
        )

        expect(attachedDIDs).toEqual(mockAttachedFiles);
    })
})

describe('fetchDIDDetails', () => {
    test('should call /did endpoint with query', async () => {
        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        const mockDIDDetails: FileDIDDetails[] = [
            { did: 'scope:name1', size: 123, status: 'OK', path: '/eos/rucio/1' },
            { did: 'scope:name2', size: 123, status: 'NOT_AVAILABLE' },
            { did: 'scope:name3', size: 123, status: 'REPLICATING' },
        ]

        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve(mockDIDDetails));

        const actions = new Actions();
        const attachedDIDs = await actions.fetchDIDDetails('atlas', 'scope:name');

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringMatching(/(\b(did|did=scope%3Aname|namespace=atlas)\b.*){3,}/)
        )

        expect(attachedDIDs).toEqual(mockDIDDetails);
    })
})

describe('getFileDIDDetails', () => {
    test('polling disabled, file DID exists in store, should not fetch', async () => {
        const mockFileDetails: FileDIDDetails = {
            status: 'OK',
            did: 'scope:name1',
            path: '/eos/rucio/1',
            size: 123
        };

        const mockGetRawState = UIStore.getRawState as jest.MockedFunction<typeof UIStore.getRawState>;
        mockGetRawState.mockClear();
        mockGetRawState.mockReturnValue({
            fileDetails: {
                'scope:name1': mockFileDetails
            },
            containerDetails: {}
        });

        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve([]));

        const actions = new Actions();
        const fileDIDDetails = await actions.getFileDIDDetails('atlas', 'scope:name1');

        expect(fileDIDDetails).toEqual(mockFileDetails);
        expect(mockRequestAPI).toBeCalledTimes(0);
    })

    test('polling disabled, file DID not exists in store, should fetch', async () => {
        const mockFileDetails: FileDIDDetails = {
            status: 'OK',
            did: 'scope:name1',
            path: '/eos/rucio/1',
            size: 123
        };

        const mockGetRawState = UIStore.getRawState as jest.MockedFunction<typeof UIStore.getRawState>;
        mockGetRawState.mockClear();
        mockGetRawState.mockReturnValue({
            fileDetails: {},
            containerDetails: {}
        });

        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve([mockFileDetails]));

        const mockUpdateState = UIStore.update as jest.MockedFunction<typeof UIStore.update>;
        mockUpdateState.mockClear();

        const actions = new Actions();
        const fileDIDDetails = await actions.getFileDIDDetails('atlas', 'scope:name1');

        expect(fileDIDDetails).toEqual(mockFileDetails);
        expect(mockRequestAPI).toBeCalled();
        expect(mockUpdateState).toBeCalled();
    })

    test('polling enabled, file DID exists in store, should fetch', async () => {
        const mockFileDetails: FileDIDDetails = {
            status: 'OK',
            did: 'scope:name1',
            path: '/eos/rucio/1',
            size: 123
        };

        const mockGetRawState = UIStore.getRawState as jest.MockedFunction<typeof UIStore.getRawState>;
        mockGetRawState.mockClear();
        mockGetRawState.mockReturnValue({
            fileDetails: {
                'scope:name1': { ...mockFileDetails, status: 'NOT_AVAILABLE', path: undefined }
            },
            containerDetails: {}
        });

        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve([mockFileDetails]));

        const mockUpdateState = UIStore.update as jest.MockedFunction<typeof UIStore.update>;
        mockUpdateState.mockClear();

        const actions = new Actions();
        const fileDIDDetails = await actions.getFileDIDDetails('atlas', 'scope:name1', true);

        expect(fileDIDDetails).toEqual(mockFileDetails);
        expect(mockRequestAPI).toBeCalled();
        expect(mockUpdateState).toBeCalled();
    })
})

describe('getContainerDIDDetails', () => {
    test('polling disabled, container DID exists in store, should not fetch', async () => {
        const mockFileDetails: FileDIDDetails = {
            status: 'OK',
            did: 'scope:name1',
            path: '/eos/rucio/1',
            size: 123
        };

        const mockGetRawState = UIStore.getRawState as jest.MockedFunction<typeof UIStore.getRawState>;
        mockGetRawState.mockClear();
        mockGetRawState.mockReturnValue({
            fileDetails: {},
            containerDetails: {
                'scope:name': [mockFileDetails]
            }
        });

        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve([]));

        const actions = new Actions();
        const fileDIDDetails = await actions.getContainerDIDDetails('atlas', 'scope:name');

        expect(fileDIDDetails).toEqual([mockFileDetails]);
        expect(mockRequestAPI).toBeCalledTimes(0);
    })

    test('polling disabled, container DID not exists in store, should fetch', async () => {
        const mockFileDetails: FileDIDDetails = {
            status: 'OK',
            did: 'scope:name1',
            path: '/eos/rucio/1',
            size: 123
        };

        const mockGetRawState = UIStore.getRawState as jest.MockedFunction<typeof UIStore.getRawState>;
        mockGetRawState.mockClear();
        mockGetRawState.mockReturnValue({
            fileDetails: {},
            containerDetails: {}
        });

        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve([mockFileDetails]));

        const mockUpdateState = UIStore.update as jest.MockedFunction<typeof UIStore.update>;
        mockUpdateState.mockClear();

        const actions = new Actions();
        const fileDIDDetails = await actions.getContainerDIDDetails('atlas', 'scope:name');

        expect(fileDIDDetails).toEqual([mockFileDetails]);
        expect(mockRequestAPI).toBeCalled();
        expect(mockUpdateState).toBeCalled();
    })

    test('polling enabled, container DID exists in store, should fetch', async () => {
        const mockFileDetails: FileDIDDetails = {
            status: 'OK',
            did: 'scope:name1',
            path: '/eos/rucio/1',
            size: 123
        };

        const mockGetRawState = UIStore.getRawState as jest.MockedFunction<typeof UIStore.getRawState>;
        mockGetRawState.mockClear();
        mockGetRawState.mockReturnValue({
            fileDetails: {},
            containerDetails: {
                'scope:name': [{ ...mockFileDetails, status: 'NOT_AVAILABLE', path: undefined }]
            }
        });

        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve([mockFileDetails]));

        const mockUpdateState = UIStore.update as jest.MockedFunction<typeof UIStore.update>;
        mockUpdateState.mockClear();

        const actions = new Actions();
        const fileDIDDetails = await actions.getContainerDIDDetails('atlas', 'scope:name', true);

        expect(fileDIDDetails).toEqual([mockFileDetails]);
        expect(mockRequestAPI).toBeCalled();
        expect(mockUpdateState).toBeCalled();
    })
})

describe('makeFileAvailable', () => {
    test('should call /did/make-available endpoint with method POST', async () => {
        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;

        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve());

        const mockUpdateState = UIStore.update as jest.MockedFunction<typeof UIStore.update>;
        mockUpdateState.mockClear();

        const actions = new Actions();
        await actions.makeFileAvailable('atlas', 'scope:name');

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringMatching(/(\b(did\/make-available|namespace=atlas)\b.*){2,}/),
            expect.objectContaining({
                method: 'POST',
                body: JSON.stringify({ did: 'scope:name' })
            })
        )

        expect(mockUpdateState).toBeCalled();
    })
})

describe('makeContainerAvailable', () => {
    test('should call /did/make-available endpoint with method POST', async () => {
        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;

        mockRequestAPI.mockClear();
        mockRequestAPI.mockReturnValue(Promise.resolve());

        const mockUpdateState = UIStore.update as jest.MockedFunction<typeof UIStore.update>;
        mockUpdateState.mockClear();

        const actions = new Actions();
        await actions.makeContainerAvailable('atlas', 'scope:name');

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringMatching(/(\b(did\/make-available|namespace=atlas)\b.*){2,}/),
            expect.objectContaining({
                method: 'POST',
                body: JSON.stringify({ did: 'scope:name' })
            })
        )

        expect(mockUpdateState).toBeCalled();
    })
})