/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 */

import { JupyterFrontEnd, ILabShell } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import extension from '../index';
import { CommandIDs } from '../const';
import uploadFile from '../commands/uploadFile';
import { actions } from '../utils/Actions';

jest.mock('@jupyterlab/application', () => ({ ILabShell: {} }));
jest.mock('@jupyterlab/notebook', () => ({ INotebookTracker: {} }));
jest.mock('@jupyterlab/filebrowser', () => ({ IFileBrowserFactory: {} }));
jest.mock('@jupyterlab/ui-components', () => ({ fileUploadIcon: {} }));
jest.mock('../widgets/SidebarPanel', () => ({ SidebarPanel: jest.fn() }));
jest.mock('../utils/NotebookListener', () => ({ NotebookListener: jest.fn() }));
jest.mock('../utils/ActiveNotebookListener', () => ({
  ActiveNotebookListener: jest.fn()
}));
jest.mock('../utils/NotebookPollingListener', () => ({
  NotebookPollingListener: jest.fn()
}));
jest.mock('../utils/Actions', () => ({
  actions: { fetchInstancesConfig: jest.fn() }
}));
jest.mock('../commands/uploadFile', () => ({
  __esModule: true,
  default: jest.fn()
}));

describe('file-browser upload command', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.mocked(actions.fetchInstancesConfig).mockResolvedValue({
      instances: []
    });
  });

  async function executeUpload(
    selection: { name: string; type: string }[] | null
  ) {
    const addCommand = jest.fn();
    const app = {
      commands: { addCommand },
      contextMenu: { addItem: jest.fn() },
      serviceManager: { sessions: {} }
    } as unknown as JupyterFrontEnd;
    const shell = {
      add: jest.fn(),
      activateById: jest.fn()
    } as unknown as ILabShell;
    const factory = {
      tracker: {
        currentWidget:
          selection === null
            ? null
            : { selectedItems: () => selection.values() }
      }
    } as unknown as IFileBrowserFactory;

    await extension.activate(app, shell, {} as INotebookTracker, factory);
    const registration = addCommand.mock.calls.find(
      ([id]) => id === CommandIDs.UploadFile
    );
    expect(registration).toBeDefined();
    await registration![1].execute();
  }

  test('uploads a selected notebook', async () => {
    const notebook = { name: 'analysis.ipynb', type: 'notebook' };
    await executeUpload([notebook]);
    expect(uploadFile).toHaveBeenCalledWith([notebook]);
  });

  test('uploads files and notebooks while excluding directories', async () => {
    const file = { name: 'data.txt', type: 'file' };
    const notebook = { name: 'analysis.ipynb', type: 'notebook' };
    const directory = { name: 'folder', type: 'directory' };
    await executeUpload([file, directory, notebook]);
    expect(uploadFile).toHaveBeenCalledWith([file, notebook]);
  });

  test.each([[], [{ name: 'folder', type: 'directory' }], null])(
    'does not upload an empty selection, directories only, or a missing browser (%j)',
    async selection => {
      await executeUpload(selection);
      expect(uploadFile).not.toHaveBeenCalled();
    }
  );
});
