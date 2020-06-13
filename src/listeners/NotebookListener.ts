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

  setup() {
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

      state.activeNotebookPanel.sessionContext.ready.then(() => {
        this.triggerKernelVariableInjection();
      });
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

    if (!activeNotebookPanel.sessionContext.session) {
      return;
    }

    const notYetInjectedAttachments = this.getNotYetInjectedAttachments();

    notYetInjectedAttachments.forEach(attachment => {
      const { type } = attachment;
      if (type === 'container') {
        this.injectContainerAttachment(attachment).catch(e => console.log(e));
      } else {
        this.injectFileAttachment(attachment).catch(e => console.log(e));
      }
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

  private injectContainerAttachment(
    attachment: NotebookDIDAttachment
  ): Promise<any> {
    const { did } = attachment;
    const { activeNotebookPanel } = ExtensionStore.getRawState();
    const comm = activeNotebookPanel.sessionContext.session.kernel.createComm(
      COMM_NAME_KERNEL
    );
    return comm
      .open()
      .done.then(() => {
        return this.resolveContainerDIDDetails(did);
      })
      .then(didDetails => {
        const paths = didDetails.map(d => d.path);
        const toSend = {
          variableName: attachment.variableName,
          path: paths
        };
        return toSend;
      })
      .then(toSend => {
        return comm.send({ action: 'inject', dids: [toSend] });
      })
      .then(() => {
        return comm.close();
      });
  }

  private injectFileAttachment(attachment: NotebookDIDAttachment) {
    const { did } = attachment;
    const { activeNotebookPanel } = ExtensionStore.getRawState();
    const comm = activeNotebookPanel.sessionContext.session.kernel.createComm(
      COMM_NAME_KERNEL
    );
    return comm
      .open()
      .done.then(() => {
        return this.resolveFileDIDDetails(did);
      })
      .then(didDetails => {
        const toSend = {
          variableName: attachment.variableName,
          path: didDetails.path
        };
        return toSend;
      })
      .then(toSend => {
        return comm.send({ action: 'inject', dids: [toSend] });
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
