jest.mock('../src/utils/ApiRequest');
import { requestAPI } from '../src/utils/ApiRequest';
import { Actions } from '../src/utils/Actions';
import { Instance, AttachedFile, FileDIDDetails } from '../src/types';

describe('fetchInstancesConfig', () => {
    test('should call /instances endpoint', async () => {
        const mockRequestAPI = requestAPI as jest.MockedFunction<typeof requestAPI>;
        const mockInstanceConfig = {
            activeInstance: 'atlas',
            instances: [] as Instance[]
        };

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

        mockRequestAPI.mockReturnValue(Promise.resolve());

        const actions = new Actions();
        await actions.postActiveInstance('atlas');

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringContaining('instances'),
            expect.objectContaining({
                method: 'PUT',
                body: JSON.stringify({
                    instance: 'atlas'
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

        mockRequestAPI.mockReturnValue(Promise.resolve(mockDIDDetails));

        const actions = new Actions();
        const attachedDIDs = await actions.fetchDIDDetails('atlas', 'scope:name');

        expect(mockRequestAPI).toBeCalledWith(
            expect.stringMatching(/(\b(did|did=scope%3Aname|namespace=atlas)\b.*){3,}/)
        )

        expect(attachedDIDs).toEqual(mockDIDDetails);
    })
})