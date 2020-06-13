import { ILabShell } from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { ExtensionStore, ExtensionState } from '../stores/ExtensionStore';
import { UIStore } from '../stores/UIStore';
import { NotebookDIDAttachment, FileDIDDetails } from '../types';
import { METADATA_KEY, COMM_NAME_KERNEL, COMM_NAME_FRONTEND } from '../const';
import { ReadonlyPartialJSONArray } from '@lumino/coreutils';
import { Actions } from '../utils/Actions';
import { SessionManager } from '@jupyterlab/services';
import { IKernelConnection } from '@jupyterlab/services/lib/kernel/kernel';

interface NotebookVariableInjection {
  variableName: string;
  path: string | string[];
}

interface AttachmentResolveIntermediate {
  attachment: NotebookDIDAttachment;
  didDetails: FileDIDDetails | FileDIDDetails[];
}

export interface NotebookListenerOptions {
  labShell: ILabShell;
  notebookTracker: INotebookTracker;
  sessionManager: SessionManager;
}

export class NotebookListener {
  options: NotebookListenerOptions;
  injectedVariableNames: { [kernelConnectionId: string]: string[] };
  actions: Actions;

  constructor(options: NotebookListenerOptions) {
    this.options = options;
    this.injectedVariableNames = {};
    this.actions = new Actions();
  }

  setup(): void {
    const { labShell, notebookTracker } = this.options;
    ExtensionStore.subscribe(
      s => s.activeNotebookAttachment,
      (attachments, state) =>
        this.onNotebookAttachmentChanged(attachments, state)
    );
    labShell.currentChanged.connect(this.onCurrentTabChanged, this);
    notebookTracker.widgetAdded.connect(this.onNotebookOpened, this);
  }

  private onCurrentTabChanged() {
    if (!this.isCurrentTabANotebook()) {
      this.setActiveNotebook(undefined);
      this.setActiveNotebookAttachments(undefined);
      return;
    }

    const { notebookTracker } = this.options;
    const nbWidget = notebookTracker.currentWidget;

    nbWidget.revealed.then(() => {
      this.setActiveNotebook(nbWidget);
      const rucioDidAttachments = nbWidget.model.metadata.get(METADATA_KEY);
      if (!rucioDidAttachments) {
        this.setActiveNotebookAttachments([]);
        return;
      }

      const attachedDIDs = rucioDidAttachments as ReadonlyArray<any>;
      this.setActiveNotebookAttachments(
        attachedDIDs as NotebookDIDAttachment[]
      );
    });
  }

  private isCurrentTabANotebook() {
    const { labShell, notebookTracker } = this.options;
    const widget = labShell.currentWidget;
    const nbWidget = notebookTracker.currentWidget;

    return !!widget && widget === nbWidget;
  }

  private setActiveNotebook(activeNotebook?: NotebookPanel): void {
    ExtensionStore.update(s => {
      s.activeNotebookPanel = activeNotebook;
    });
  }

  private setActiveNotebookAttachments(attachments: NotebookDIDAttachment[]) {
    ExtensionStore.update(s => {
      s.activeNotebookAttachment = attachments;
    });
  }

  private onNotebookAttachmentChanged(
    attachments: NotebookDIDAttachment[],
    state: ExtensionState
  ) {
    if (attachments && state.activeNotebookPanel) {
      this.setJupyterNotebookFileRucioMetadata(attachments, state);
      this.triggerKernelVariableInjection();
    }
  }

  private setJupyterNotebookFileRucioMetadata(
    attachments: NotebookDIDAttachment[],
    state: ExtensionState
  ) {
    const { metadata } = state.activeNotebookPanel.model;
    const current = metadata.get(METADATA_KEY) as ReadonlyArray<any>;
    const rucioDidAttachments = attachments as ReadonlyArray<any>;

    if (current !== rucioDidAttachments) {
      metadata.set(
        METADATA_KEY,
        rucioDidAttachments as ReadonlyPartialJSONArray
      );
    }
  }

  private onNotebookOpened(sender: INotebookTracker, panel: NotebookPanel) {
    panel.sessionContext.statusChanged.connect((sender, status) => {
      if (status === 'restarting') {
        this.onKernelRestarted(sender.session.kernel);
      }
    });
    panel.sessionContext.kernelChanged.connect((sender, changed) => {
      const oldKernel = changed.oldValue;
      if (oldKernel) {
        this.onKernelDetached(oldKernel);
      }

      const newKernel = changed.newValue;
      if (newKernel) {
        this.onKernelAttached(newKernel);
      }
    });
  }

  private onKernelRestarted(kernelConnection: IKernelConnection) {
    this.clearInjectedVariableNames(kernelConnection.id);
  }

  private onKernelDetached(kernelConnection: IKernelConnection) {
    this.clearInjectedVariableNames(kernelConnection.id);
  }

  private onKernelAttached(kernelConnection: IKernelConnection) {
    this.setupKernelReceiverComm(kernelConnection);
  }

  private setupKernelReceiverComm(kernelConnection: IKernelConnection) {
    kernelConnection.registerCommTarget(COMM_NAME_FRONTEND, (comm, openMsg) => {
      const data = openMsg.content.data;
      if (data.action === 'request-inject') {
        this.triggerKernelVariableInjection();
      } else if (data.action === 'ack-inject') {
        const kernelConnectionId = kernelConnection.id;
        const variableNames = data.variable_names as string[];
        this.appendInjectedVariableNames(kernelConnectionId, variableNames);
      }
    });
  }

  private appendInjectedVariableNames(
    kernelConnectionId: string,
    variableNames: string[]
  ) {
    const injectedVariableNames =
      this.injectedVariableNames[kernelConnectionId] || [];
    this.injectedVariableNames[kernelConnectionId] = [
      ...injectedVariableNames,
      ...variableNames
    ];
  }

  private clearInjectedVariableNames(kernelConnectionId: string) {
    delete this.injectedVariableNames[kernelConnectionId];
  }

  private triggerKernelVariableInjection() {
    const { activeNotebookPanel } = ExtensionStore.getRawState();

    activeNotebookPanel.sessionContext.ready.then(() => {
      if (!activeNotebookPanel.sessionContext.session) {
        return;
      }

      const notYetInjectedAttachments = this.getNotYetInjectedAttachments();
      const promises = notYetInjectedAttachments.map(attachment =>
        this.createAttachmentResolvePromise(attachment)
      );

      return Promise.all(promises)
        .then(attributes => {
          return attributes.map(({ attachment, didDetails }) => {
            const { variableName, type } = attachment;
            const path =
              type === 'container'
                ? this.getContainerDIDPaths(didDetails as FileDIDDetails[])
                : this.getFileDIDPaths(didDetails as FileDIDDetails);

            return { variableName: variableName, path };
          });
        })
        .then(dids => {
          return this.injectAttachments(dids);
        });
    });
  }

  private getNotYetInjectedAttachments() {
    const {
      activeNotebookPanel,
      activeNotebookAttachment
    } = ExtensionStore.getRawState();

    const kernelConnectionId =
      activeNotebookPanel.sessionContext.session.kernel.id;
    const injectedVariableNames =
      this.injectedVariableNames[kernelConnectionId] || [];
    const attachments = activeNotebookAttachment || [];

    return attachments.filter(
      a => !injectedVariableNames.includes(a.variableName)
    );
  }

  private createAttachmentResolvePromise(
    attachment: NotebookDIDAttachment
  ): Promise<AttachmentResolveIntermediate> {
    const retrieveFunction = async () => {
      if (attachment.type === 'container') {
        const didDetails = await this.resolveContainerDIDDetails(
          attachment.did
        );
        return { attachment, didDetails };
      } else {
        const didDetails = await this.resolveFileDIDDetails(attachment.did);
        return { attachment, didDetails };
      }
    };

    return retrieveFunction();
  }

  private getContainerDIDPaths(didDetails: FileDIDDetails[]): string[] {
    return didDetails.map(d => d.path).filter(p => !!p);
  }

  private getFileDIDPaths(didDetails: FileDIDDetails): string {
    return didDetails.path;
  }

  private injectAttachments(
    injections: NotebookVariableInjection[]
  ): Promise<any> {
    const { activeNotebookPanel } = ExtensionStore.getRawState();
    const comm = activeNotebookPanel.sessionContext.session.kernel.createComm(
      COMM_NAME_KERNEL
    );

    return comm
      .open()
      .done.then(() => {
        return comm.send({ action: 'inject', dids: injections as any[] });
      })
      .then(() => {
        return comm.close();
      });
  }

  private async resolveFileDIDDetails(did: string): Promise<FileDIDDetails> {
    const { activeInstance } = UIStore.getRawState();
    return this.actions.getFileDIDDetails(activeInstance.name, did);
  }

  private async resolveContainerDIDDetails(
    did: string
  ): Promise<FileDIDDetails[]> {
    const { activeInstance } = UIStore.getRawState();
    return this.actions.getContainerDIDDetails(activeInstance.name, did);
  }
}
