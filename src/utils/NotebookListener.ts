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

import { ILabShell } from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { SessionManager, KernelMessage, Kernel } from '@jupyterlab/services';
import { IKernelConnection } from '@jupyterlab/services/lib/kernel/kernel';
import { Store, useStoreState } from 'pullstate';
import { UIStore } from '../stores/UIStore';
import { NotebookDIDAttachment, FileDIDDetails, ResolveStatus } from '../types';
import { COMM_NAME_KERNEL, COMM_NAME_FRONTEND, METADATA_ATTACHMENTS_KEY } from '../const';
import { actions } from '../utils/Actions';
import { InjectNotebookToolbar } from '../InjectNotebookToolbar';
import { computeCollectionState } from './Helpers';

type InjectedFile = {
  path: string;
  pfn?: string;
};

interface NotebookVariableInjection {
  type: 'file' | 'collection';
  variableName: string;
  files: Array<InjectedFile> | null;
  did: string;
  didAvailable: boolean;
}

type StatusMap = { [notebookId: string]: { [did: string]: ResolveStatus } };
type StatusState = {
  status: StatusMap;
};
const StatusStore = new Store<StatusState>({ status: {} });

export function useNotebookResolveStatusStore(): StatusMap {
  const resolveStatus = useStoreState(StatusStore, s => s.status);
  return resolveStatus;
}

export interface NotebookListenerOptions {
  labShell: ILabShell;
  notebookTracker: INotebookTracker;
  sessionManager: SessionManager;
}

export class NotebookListener {
  options: NotebookListenerOptions;
  kernelNotebookMapping: { [kernelConnectionId: string]: string } = {};

  constructor(options: NotebookListenerOptions) {
    this.options = options;
    this.setup();
  }

  private setup(): void {
    const { notebookTracker } = this.options;

    const instanceConfigurationChange = () => {
      StatusStore.update(s => {
        s.status = {};
      });

      notebookTracker.forEach(p => this.reinject(p));
    };

    UIStore.subscribe(
      s => s.activeInstance,
      activeInstance => {
        if (activeInstance) {
          instanceConfigurationChange();
        }
      }
    );

    notebookTracker.widgetAdded.connect(this.onNotebookOpened, this);
  }

  private onNotebookOpened(sender: INotebookTracker, panel: NotebookPanel) {
    panel.sessionContext.statusChanged.connect((sender, status) => {
      if (status === 'restarting') {
        const kernel = sender.session?.kernel;

        if (kernel) {
          this.onKernelRestarted(panel, kernel);
        }
        panel.sessionContext.ready.then(() => {
          if (kernel) {
            this.onKernelAttached(panel, kernel);
          }
        });
      }
    });
    panel.sessionContext.kernelChanged.connect((sender, changed) => {
      const oldKernel = changed.oldValue;
      if (oldKernel) {
        this.onKernelDetached(panel, oldKernel);
      }

      const newKernel = changed.newValue;
      if (newKernel) {
        panel.sessionContext.ready.then(() => {
          this.onKernelAttached(panel, newKernel);
        });
      }
    });

    this.insertInjectButton(panel);
  }

  private insertInjectButton(notebookPanel: NotebookPanel) {
    const onClick = () => {
      if (notebookPanel.sessionContext?.session?.kernel) {
        this.reinject(notebookPanel);
      }
    };
    const injectNotebookButtonWidget = new InjectNotebookToolbar({ notebookPanel, onClick });
    notebookPanel.toolbar.insertAfter('spacer', 'InjectButton', injectNotebookButtonWidget);
  }

  private onKernelRestarted(notebook: NotebookPanel, kernelConnection: IKernelConnection) {
    this.clearKernelResolverStatus(kernelConnection.id);
  }

  private onKernelDetached(notebook: NotebookPanel, kernelConnection: IKernelConnection) {
    this.clearKernelResolverStatus(kernelConnection.id);
    this.deleteKernelNotebookMapping(kernelConnection.id);
  }

  private onKernelAttached(notebook: NotebookPanel, kernelConnection: IKernelConnection) {
    this.setKernelNotebookMapping(kernelConnection.id, notebook.id);
    this.setupKernelReceiverComm(kernelConnection);

    const activeNotebookAttachments = this.getAttachmentsFromMetadata(notebook);
    this.injectAttachments(kernelConnection, activeNotebookAttachments);
  }

  private clearKernelResolverStatus(kernelConnectionId: string) {
    const notebookId = this.getNotebookIdFromKernelConnectionId(kernelConnectionId);
    StatusStore.update(s => {
      s.status[notebookId] = {};
    });
  }

  private setupKernelReceiverComm(kernelConnection: IKernelConnection) {
    kernelConnection.registerCommTarget(COMM_NAME_FRONTEND, (comm, openMsg) => {
      comm.onMsg = msg => {
        this.processIncomingMessage(kernelConnection, comm, msg);
      };
      this.processIncomingMessage(kernelConnection, comm, openMsg);
    });
  }

  private processIncomingMessage(
    kernelConnection: IKernelConnection,
    comm: Kernel.IComm,
    msg: KernelMessage.ICommMsgMsg | KernelMessage.ICommOpenMsg
  ) {
    const data = msg.content.data;
    if (data.action === 'request-inject') {
      const { activeInstance } = UIStore.getRawState();
      const notebookId = this.getNotebookIdFromKernelConnectionId(kernelConnection.id);
      const { notebookTracker } = this.options;
      const notebook = notebookTracker.find(p => p.id === notebookId);

      if (!notebook || !activeInstance) {
        return;
      }

      const activeNotebookAttachments = this.getAttachmentsFromMetadata(notebook);

      this.resolveAttachments(activeNotebookAttachments, kernelConnection.id).then(injections => {
        return comm
          .send({ action: 'inject', dids: injections as any })
          .done.then(() => {
            injections.forEach(injection => this.setResolveStatus(kernelConnection.id, injection.did, 'READY'));
          })
          .catch(e => {
            console.error(e);
            injections.forEach(injection => this.setResolveStatus(kernelConnection.id, injection.did, 'FAILED'));
          });
      });
    }
  }

  injectUninjected(notebookPanel: NotebookPanel): void {
    const attachments = this.getAttachmentsFromMetadata(notebookPanel);
    const kernel = notebookPanel.sessionContext?.session?.kernel;

    if (kernel) {
      this.injectUninjectedAttachments(kernel, attachments);
      this.removeNonExistentInjectedAttachments(kernel?.id, attachments);
    }
  }

  reinject(notebookPanel: NotebookPanel): void {
    const attachments = this.getAttachmentsFromMetadata(notebookPanel);
    const kernel = notebookPanel.sessionContext?.session?.kernel;
    if (kernel) {
      this.injectAttachments(kernel, attachments);
    }
  }

  reinjectSpecificDID(notebookPanel: NotebookPanel, did: string): void {
    const attachments = this.getAttachmentsFromMetadata(notebookPanel);
    const didAttachment = attachments.find(a => a.did === did);
    const kernel = notebookPanel.sessionContext?.session?.kernel;

    if (kernel && didAttachment) {
      this.injectAttachments(kernel, [didAttachment]);
    }
  }

  private getAttachmentsFromMetadata(notebook: NotebookPanel): NotebookDIDAttachment[] {
    const rucioDidAttachments = notebook.model?.metadata.get(METADATA_ATTACHMENTS_KEY) ?? [];
    const attachedDIDs = rucioDidAttachments as ReadonlyArray<any>;
    return attachedDIDs as NotebookDIDAttachment[];
  }

  private injectUninjectedAttachments(kernel: Kernel.IKernelConnection, attachments: NotebookDIDAttachment[]) {
    const kernelConnectionId = kernel?.id;
    const notebookId = this.getNotebookIdFromKernelConnectionId(kernelConnectionId);
    const notebookStatus = StatusStore.getRawState().status[notebookId] || {};
    const uninjectedAttachments = attachments.filter(a => !notebookStatus[a.did]);
    this.injectAttachments(kernel, uninjectedAttachments);
  }

  private removeNonExistentInjectedAttachments(kernelConnectionId: string, attachments: NotebookDIDAttachment[]) {
    const notebookId = this.getNotebookIdFromKernelConnectionId(kernelConnectionId);
    StatusStore.update(s => {
      const notebookStatus = s.status[notebookId];
      if (notebookStatus) {
        const injectedDIDs = Object.keys(notebookStatus);
        const nonExistentDIDs = injectedDIDs.filter(did => !attachments.find(a => a.did === did));
        nonExistentDIDs.forEach(nd => delete s.status[notebookId][nd]);
      }
    });
  }

  private injectAttachments(kernel: Kernel.IKernelConnection, attachments: NotebookDIDAttachment[]) {
    if (!this.isExtensionProperlySetup() || !attachments) {
      return;
    }

    this.resolveAttachments(attachments, kernel.id)
      .then(injections => {
        return this.injectVariables(kernel, injections);
      })
      .then(() => {
        attachments.forEach(attachment => this.setResolveStatus(kernel.id, attachment.did, 'READY'));
      })
      .catch(e => {
        console.error(e);
        attachments.forEach(attachment => this.setResolveStatus(kernel.id, attachment.did, 'FAILED'));
      });
  }

  private injectVariables(kernel: Kernel.IKernelConnection, injections: NotebookVariableInjection[]): Promise<any> {
    if (injections.length === 0) {
      return Promise.resolve();
    }

    const comm = kernel.createComm(COMM_NAME_KERNEL);
    return comm
      .open()
      .done.then(() => comm.send({ action: 'inject', dids: injections as any[] }).done)
      .then(() => comm.close().done);
  }

  private async resolveAttachments(
    attachments: NotebookDIDAttachment[],
    kernelConnectionId: string
  ): Promise<NotebookVariableInjection[]> {
    const promises = attachments.map(a => this.resolveAttachment(a, kernelConnectionId));
    return Promise.all(promises);
  }

  private async resolveAttachment(
    attachment: NotebookDIDAttachment,
    kernelConnectionId: string
  ): Promise<NotebookVariableInjection> {
    const { variableName, type, did } = attachment;
    this.setResolveStatus(kernelConnectionId, did, 'RESOLVING');
    try {
      if (type === 'collection') {
        const didDetails = await this.resolveCollectionDIDDetails(did);
        const files = this.getCollectionFiles(didDetails);

        this.setResolveStatus(kernelConnectionId, did, 'PENDING_INJECTION');

        const collectionStatus = computeCollectionState(didDetails);
        const didAvailable = collectionStatus === 'AVAILABLE';

        return { type: 'collection', variableName, files, did, didAvailable };
      } else {
        const didDetails = await this.resolveFileDIDDetails(did);
        const file = this.getFile(didDetails);

        this.setResolveStatus(kernelConnectionId, did, 'PENDING_INJECTION');

        const fileStatus = didDetails.status;
        const didAvailable = fileStatus === 'OK';

        return { type: 'file', variableName, files: file ? [file] : null, did, didAvailable };
      }
    } catch (e) {
      this.setResolveStatus(kernelConnectionId, did, 'FAILED');
      throw e;
    }
  }

  private setResolveStatus(kernelConnectionId: string, did: string, status: ResolveStatus) {
    const notebookId = this.getNotebookIdFromKernelConnectionId(kernelConnectionId);
    StatusStore.update(s => {
      if (!s.status[notebookId]) {
        s.status[notebookId] = {};
      }

      s.status[notebookId][did] = status;
    });
  }

  private getCollectionFiles(didDetails: FileDIDDetails[]): InjectedFile[] {
    return didDetails.map(d => this.getFile(d)).filter(p => !!p) as InjectedFile[];
  }

  private getFile(didDetails: FileDIDDetails): InjectedFile | null {
    if (!didDetails.path) {
      return null;
    }

    return { path: didDetails.path, pfn: didDetails.pfn };
  }

  private async resolveFileDIDDetails(did: string): Promise<FileDIDDetails> {
    const { activeInstance } = UIStore.getRawState();
    if (!activeInstance) {
      throw new Error('activeInstance cannot be empty');
    }

    return actions.getFileDIDDetails(activeInstance.name, did);
  }

  private async resolveCollectionDIDDetails(did: string): Promise<FileDIDDetails[]> {
    const { activeInstance } = UIStore.getRawState();
    if (!activeInstance) {
      throw new Error('activeInstance cannot be empty');
    }

    return actions.getCollectionDIDDetails(activeInstance.name, did);
  }

  private getNotebookIdFromKernelConnectionId(kernelConnectionId: string) {
    return this.kernelNotebookMapping[kernelConnectionId];
  }

  private setKernelNotebookMapping(kernelConnectionId: string, notebookId: string) {
    this.kernelNotebookMapping[kernelConnectionId] = notebookId;
  }

  private deleteKernelNotebookMapping(kernelConnectionId: string) {
    delete this.kernelNotebookMapping[kernelConnectionId];
  }

  private isExtensionProperlySetup() {
    const { activeInstance } = UIStore.getRawState();
    return !!activeInstance;
  }
}
