import { ILabShell } from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { ExtensionStore, ExtensionState } from '../stores/ExtensionStore';
import { UIStore } from '../stores/UIStore';
import { NotebookDIDAttachment, FileDIDDetails } from '../types';
import { METADATA_KEY, COMM_NAME_KERNEL, COMM_NAME_FRONTEND } from '../const';
import { ReadonlyPartialJSONArray } from '@lumino/coreutils';
import { Actions } from '../utils/Actions';
import { SessionManager, KernelMessage, Kernel } from '@jupyterlab/services';
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

    const instanceConfigurationChange = () => {
      console.log('[Listener] Instance config changed!');

      this.injectedVariableNames = {};
      const state = ExtensionStore.getRawState();
      this.onNotebookAttachmentChanged(state.activeNotebookAttachment, state);
    };

    UIStore.subscribe(
      s => s.activeInstance,
      activeInstance => {
        if (activeInstance) {
          instanceConfigurationChange();
        }
      }
    );

    ExtensionStore.subscribe(
      s => s.activeNotebookAttachment,
      (attachments, state) => {
        this.onNotebookAttachmentChanged(attachments, state);
      }
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
      this.setActiveNotebookAttachments(attachedDIDs as NotebookDIDAttachment[]);
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

  private onNotebookAttachmentChanged(attachments: NotebookDIDAttachment[], state: ExtensionState) {
    const { activeNotebookPanel } = state;

    if (!attachments || !activeNotebookPanel) {
      return;
    }

    if (!activeNotebookPanel.sessionContext.session?.kernel) {
      return;
    }

    this.setJupyterNotebookFileRucioMetadata(attachments, state);
    this.removeNonExistentInjectedVariableNames(attachments, state);

    activeNotebookPanel.sessionContext.ready.then(() => {
      return this.triggerInjection('Injecting due to changed attachment');
    });
  }

  private triggerInjection(debugMessage = '') {
    const { activeInstance } = UIStore.getRawState();

    if (!activeInstance) {
      return;
    }

    const attachments = this.getNotYetInjectedAttachments();
    this.createVariableInjectionPayload(attachments).then(injections => {
      console.log(debugMessage);
      return this.injectAttachments(injections);
    });
  }

  private setJupyterNotebookFileRucioMetadata(attachments: NotebookDIDAttachment[], state: ExtensionState) {
    const { metadata } = state.activeNotebookPanel.model;
    const current = metadata.get(METADATA_KEY) as ReadonlyArray<any>;
    const rucioDidAttachments = attachments as ReadonlyArray<any>;

    if (current !== rucioDidAttachments) {
      metadata.set(METADATA_KEY, rucioDidAttachments as ReadonlyPartialJSONArray);
    }
  }

  private removeNonExistentInjectedVariableNames(attachments: NotebookDIDAttachment[], state: ExtensionState) {
    const kernelConnectionId = state.activeNotebookPanel.sessionContext.session?.kernel?.id;
    const injectedVariableNames = this.injectedVariableNames[kernelConnectionId];

    if (!!kernelConnectionId && !!injectedVariableNames) {
      this.injectedVariableNames[kernelConnectionId] = injectedVariableNames.filter(n =>
        attachments.find(a => a.variableName === n)
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
        panel.sessionContext.ready.then(() => {
          this.onKernelAttached(newKernel);
        });
      }
    });
  }

  private onKernelRestarted(kernelConnection: IKernelConnection) {
    console.log('Kernel restarted', kernelConnection.id);
    this.clearInjectedVariableNames(kernelConnection.id);
  }

  private onKernelDetached(kernelConnection: IKernelConnection) {
    console.log('Kernel detached', kernelConnection.id);
    this.clearInjectedVariableNames(kernelConnection.id);
  }

  private onKernelAttached(kernelConnection: IKernelConnection) {
    console.log('Kernel attached');
    this.setupKernelReceiverComm(kernelConnection);
    this.triggerInjection('Injecting due to kernel attached');
  }

  private setupKernelReceiverComm(kernelConnection: IKernelConnection) {
    console.log('Setup receiver comm');
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
      const { activeNotebookAttachment } = ExtensionStore.getRawState();
      const { activeInstance } = UIStore.getRawState();

      if (!activeNotebookAttachment || !activeInstance) {
        return;
      }

      this.createVariableInjectionPayload(activeNotebookAttachment).then(injections => {
        console.log('Replying request-inject', injections);
        return comm.send({ action: 'inject', dids: injections }).done;
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
    console.log('Append varnames', kernelConnectionId, variableNames);
  }

  private clearInjectedVariableNames(kernelConnectionId: string) {
    delete this.injectedVariableNames[kernelConnectionId];
  }

  private async createVariableInjectionPayload(attachments: NotebookDIDAttachment[]) {
    const promises = attachments.map(attachment => this.createAttachmentResolvePromise(attachment));

    return Promise.all(promises).then(attributes => {
      return attributes.map(({ attachment, didDetails }) => {
        const { variableName, type } = attachment;
        const path =
          type === 'container'
            ? this.getContainerDIDPaths(didDetails as FileDIDDetails[])
            : this.getFileDIDPaths(didDetails as FileDIDDetails);

        return { variableName: variableName, path };
      });
    });
  }

  private getNotYetInjectedAttachments() {
    const { activeNotebookPanel, activeNotebookAttachment } = ExtensionStore.getRawState();

    const kernelConnectionId = activeNotebookPanel.sessionContext.session.kernel.id;
    const injectedVariableNames = this.injectedVariableNames[kernelConnectionId] || [];
    const attachments = activeNotebookAttachment || [];

    return attachments.filter(a => !injectedVariableNames.includes(a.variableName));
  }

  private createAttachmentResolvePromise(attachment: NotebookDIDAttachment): Promise<AttachmentResolveIntermediate> {
    const retrieveFunction = async () => {
      if (attachment.type === 'container') {
        const didDetails = await this.resolveContainerDIDDetails(attachment.did);
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

  private injectAttachments(injections: NotebookVariableInjection[]): Promise<any> {
    console.log('Injecting variables', injections);
    if (injections.length === 0) {
      return;
    }

    const { activeNotebookPanel } = ExtensionStore.getRawState();
    const comm = activeNotebookPanel.sessionContext.session.kernel.createComm(COMM_NAME_KERNEL);

    return comm
      .open()
      .done.then(() => comm.send({ action: 'inject', dids: injections as any[] }).done)
      .then(() => comm.close().done)
      .then(() => {
        const kernelConnectionId = activeNotebookPanel.sessionContext.session.kernel.id;
        this.appendInjectedVariableNames(
          kernelConnectionId,
          injections.map(i => i.variableName)
        );
      });
  }

  private async resolveFileDIDDetails(did: string): Promise<FileDIDDetails> {
    const { activeInstance } = UIStore.getRawState();
    return this.actions.getFileDIDDetails(activeInstance.name, did);
  }

  private async resolveContainerDIDDetails(did: string): Promise<FileDIDDetails[]> {
    const { activeInstance } = UIStore.getRawState();
    return this.actions.getContainerDIDDetails(activeInstance.name, did);
  }
}
