import { ILabShell } from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { Store, useStoreState } from 'pullstate';
import { UIStore } from '../stores/UIStore';
import { NotebookDIDAttachment, FileDIDDetails, ResolveStatus } from '../types';
import { COMM_NAME_KERNEL, COMM_NAME_FRONTEND, METADATA_KEY } from '../const';
import { actions } from '../utils/Actions';
import { SessionManager, KernelMessage, Kernel } from '@jupyterlab/services';
import { IKernelConnection } from '@jupyterlab/services/lib/kernel/kernel';
import { InjectNotebookToolbar } from '../InjectNotebookToolbar';

interface NotebookVariableInjection {
  variableName: string;
  path: string | string[];
  did: string;
}

interface AttachmentResolveIntermediate {
  attachment: NotebookDIDAttachment;
  didDetails: FileDIDDetails | FileDIDDetails[];
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
  injectedVariableNames: { [kernelConnectionId: string]: string[] } = {}; // TODO migrate to Set, or just use StatusStore
  kernelNotebookMapping: { [kernelConnectionId: string]: string } = {};

  constructor(options: NotebookListenerOptions) {
    this.options = options;
    this.setup();
  }

  private setup(): void {
    const { notebookTracker } = this.options;

    const instanceConfigurationChange = () => {
      console.log('[Listener] Instance config changed!');

      this.injectedVariableNames = {};
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

  injectUninjected(notebookPanel: NotebookPanel): void {
    const attachments = this.getAttachmentsFromMetadata(notebookPanel);
    const kernel = notebookPanel.sessionContext?.session?.kernel;

    this.injectUninjectedAttachments(kernel, attachments);
    this.removeNonExistentInjectedVariableNames(kernel?.id, attachments);
  }

  reinject(notebookPanel: NotebookPanel): void {
    const attachments = this.getAttachmentsFromMetadata(notebookPanel);
    const kernel = notebookPanel.sessionContext?.session?.kernel;
    this.injectAttachments(kernel, attachments);
  }

  private getAttachmentsFromMetadata(notebook: NotebookPanel): NotebookDIDAttachment[] {
    const rucioDidAttachments = notebook.model.metadata.get(METADATA_KEY);
    const attachedDIDs = rucioDidAttachments as ReadonlyArray<any>;
    return attachedDIDs as NotebookDIDAttachment[];
  }

  private removeNonExistentInjectedVariableNames(kernelConnectionId: string, attachments: NotebookDIDAttachment[]) {
    const injectedVariableNames = this.injectedVariableNames[kernelConnectionId];

    if (!!kernelConnectionId && !!injectedVariableNames) {
      this.injectedVariableNames[kernelConnectionId] = injectedVariableNames.filter(n =>
        attachments.find(a => a.variableName === n)
      );
    }
  }

  private injectUninjectedAttachments(kernel: Kernel.IKernelConnection, attachments: NotebookDIDAttachment[]) {
    const kernelConnectionId = kernel?.id;
    const injectedVariables = this.injectedVariableNames[kernelConnectionId] || [];
    const uninjectedAttachments = attachments.filter(a => !injectedVariables.includes(a.variableName));
    this.injectAttachments(kernel, uninjectedAttachments);
  }

  private injectAttachments(kernel: Kernel.IKernelConnection, attachments: NotebookDIDAttachment[]) {
    if (!this.isExtensionProperlySetup()) {
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
      return;
    }

    const comm = kernel.createComm(COMM_NAME_KERNEL);

    return comm
      .open()
      .done.then(() => comm.send({ action: 'inject', dids: injections as any[] }).done)
      .then(() => comm.close().done)
      .then(() => {
        const kernelConnectionId = kernel.id;
        this.appendInjectedVariableNames(
          kernelConnectionId,
          injections.map(i => i.variableName)
        );
      });
  }

  private onNotebookOpened(sender: INotebookTracker, panel: NotebookPanel) {
    panel.sessionContext.statusChanged.connect((sender, status) => {
      if (status === 'restarting') {
        this.onKernelRestarted(panel, sender.session.kernel);
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
    this.clearInjectedVariableNames(kernelConnection.id);
    this.clearKernelResolverStatus(kernelConnection.id);
  }

  private onKernelDetached(notebook: NotebookPanel, kernelConnection: IKernelConnection) {
    this.clearInjectedVariableNames(kernelConnection.id);
    this.clearKernelResolverStatus(kernelConnection.id);
    delete this.kernelNotebookMapping[notebook.id];
  }

  private onKernelAttached(notebook: NotebookPanel, kernelConnection: IKernelConnection) {
    this.setupKernelReceiverComm(kernelConnection);

    const notebookId = notebook.id;
    this.kernelNotebookMapping[kernelConnection.id] = notebookId;

    const activeNotebookAttachments = this.getAttachmentsFromMetadata(notebook);
    this.injectAttachments(kernelConnection, activeNotebookAttachments);
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
    console.log('Incoming message', data);
    if (data.action === 'request-inject') {
      const { activeInstance } = UIStore.getRawState();
      const notebookId = this.kernelNotebookMapping[kernelConnection.id];
      const { notebookTracker } = this.options;
      const notebook = notebookTracker.find(p => p.id === notebookId);
      const activeNotebookAttachments = this.getAttachmentsFromMetadata(notebook);

      if (!activeNotebookAttachments || !activeInstance) {
        return;
      }

      this.resolveAttachments(activeNotebookAttachments, kernelConnection.id).then(injections => {
        console.log('Replying request-inject', injections);
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
    } else if (data.action === 'ack-inject') {
      const kernelConnectionId = kernelConnection.id;
      const variableNames = data.variable_names as string[];
      this.appendInjectedVariableNames(kernelConnectionId, variableNames);
    }
  }

  private appendInjectedVariableNames(kernelConnectionId: string, variableNames: string[]) {
    const injectedVariableNames = this.injectedVariableNames[kernelConnectionId] || [];
    this.injectedVariableNames[kernelConnectionId] = [...injectedVariableNames, ...variableNames];
  }

  private clearInjectedVariableNames(kernelConnectionId: string) {
    delete this.injectedVariableNames[kernelConnectionId];
  }

  private clearKernelResolverStatus(kernelConnectionId: string) {
    const notebookId = this.kernelNotebookMapping[kernelConnectionId];
    StatusStore.update(s => {
      s.status[notebookId] = {};
    });
  }

  private async resolveAttachments(
    attachments: NotebookDIDAttachment[],
    kernelConnectionId?: string
  ): Promise<NotebookVariableInjection[]> {
    const resolveFunction = (a: NotebookDIDAttachment) => {
      this.setResolveStatus(kernelConnectionId, a.did, 'RESOLVING');
      return this.resolveAttachment(a)
        .then(injection => {
          this.setResolveStatus(kernelConnectionId, a.did, 'PENDING_INJECTION');
          return injection;
        })
        .catch(e => {
          console.error(e);
          this.setResolveStatus(kernelConnectionId, a.did, 'FAILED');
          return null;
        });
    };

    const promises = attachments.map(a => resolveFunction(a));
    return Promise.all(promises);
  }

  private resolveAttachment(attachment: NotebookDIDAttachment): Promise<NotebookVariableInjection> {
    const retrieveFunction = async () => {
      if (attachment.type === 'container') {
        const didDetails = await this.resolveContainerDIDDetails(attachment.did);
        return this.translateIntermediateToNotebookVariableInjection({ attachment, didDetails });
      } else {
        const didDetails = await this.resolveFileDIDDetails(attachment.did);
        return this.translateIntermediateToNotebookVariableInjection({ attachment, didDetails });
      }
    };

    return retrieveFunction();
  }

  private setResolveStatus(kernelConnectionId: string, did: string, status: ResolveStatus) {
    const notebookId = this.kernelNotebookMapping[kernelConnectionId];
    StatusStore.update(s => {
      if (!s.status[notebookId]) {
        s.status[notebookId] = {};
      }

      s.status[notebookId][did] = status;
    });
  }

  private translateIntermediateToNotebookVariableInjection(
    intermediate: AttachmentResolveIntermediate
  ): NotebookVariableInjection {
    const { attachment, didDetails } = intermediate;
    const { variableName, type, did } = attachment;
    const path =
      type === 'container'
        ? this.getContainerDIDPaths(didDetails as FileDIDDetails[])
        : this.getFileDIDPaths(didDetails as FileDIDDetails);

    return { variableName: variableName, path, did };
  }

  private getContainerDIDPaths(didDetails: FileDIDDetails[]): string[] {
    return didDetails.map(d => d.path).filter(p => !!p);
  }

  private getFileDIDPaths(didDetails: FileDIDDetails): string {
    return didDetails.path;
  }

  private async resolveFileDIDDetails(did: string): Promise<FileDIDDetails> {
    const { activeInstance } = UIStore.getRawState();
    return actions.getFileDIDDetails(activeInstance.name, did);
  }

  private async resolveContainerDIDDetails(did: string): Promise<FileDIDDetails[]> {
    const { activeInstance } = UIStore.getRawState();
    return actions.getContainerDIDDetails(activeInstance.name, did);
  }

  private isExtensionProperlySetup() {
    const { activeInstance } = UIStore.getRawState();
    return !!activeInstance;
  }
}
