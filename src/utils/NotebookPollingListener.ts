import { ExtensionStore } from '../stores/ExtensionStore';
import { UIStore } from '../stores/UIStore';
import { PollingRequesterRef, didPollingManager } from './DIDPollingManager';
import { NotebookDIDAttachment } from '../types';
import { actions } from './Actions';
import { NotebookListener } from './NotebookListener';
import { computeContainerState } from './Helpers';

export class NotebookPollingListener {
  notebookListener: NotebookListener;
  pollingRef: PollingRequesterRef;
  activePolling: string[] = [];
  activeNotebookAttachmentDIDs: string[] = [];

  constructor(notebookListener: NotebookListener) {
    this.notebookListener = notebookListener;
    this.pollingRef = new PollingRequesterRef();

    // Listen to change in attachments
    ExtensionStore.subscribe(
      s => s.activeNotebookAttachment,
      attachments => {
        this.removeUnfocusedDIDs(attachments);
        this.processNewAttachments(attachments);
        this.activeNotebookAttachmentDIDs = attachments?.map(a => a.did) || [];
      }
    );

    // Listen to change in file status
    UIStore.subscribe(
      s => s.fileDetails,
      (fileDetails, state, prevFileDetails) => {
        if (!fileDetails) {
          return;
        }

        const listenedFileDetails = Object.keys(fileDetails)
          .filter(did => this.activeNotebookAttachmentDIDs.includes(did))
          .map(did => ({
            did,
            file: {
              current: fileDetails[did],
              prev: prevFileDetails[did]
            }
          }));

        listenedFileDetails.forEach(({ did, file }) => {
          if (file.current.status === 'REPLICATING') {
            this.enablePolling(did, 'file');
          } else {
            if (this.activePolling.includes(did)) {
              this.disablePolling(did);
            }
            if (file.current.status === 'OK' && file.prev?.status === 'REPLICATING') {
              const { activeNotebookPanel } = ExtensionStore.getRawState();
              this.notebookListener.reinjectSpecificDID(activeNotebookPanel, did);
            }
          }
        });
      }
    );

    // Listen to change in container status
    UIStore.subscribe(
      s => s.containerDetails,
      (containerDetails, state, prevContainerDetails) => {
        if (!containerDetails) {
          return;
        }

        const listenedContainerDetails = Object.keys(containerDetails)
          .filter(did => this.activeNotebookAttachmentDIDs.includes(did))
          .map(did => ({
            did,
            file: {
              current: containerDetails[did],
              prev: prevContainerDetails[did]
            }
          }));

        listenedContainerDetails.forEach(({ did, file }) => {
          const currentContainerState = computeContainerState(file.current);
          if (currentContainerState === 'REPLICATING') {
            this.enablePolling(did, 'container');
          } else {
            if (this.activePolling.includes(did)) {
              this.disablePolling(did);
            }
            const prevContainerState = computeContainerState(file.prev);
            if (currentContainerState === 'AVAILABLE' && prevContainerState === 'REPLICATING') {
              const { activeNotebookPanel } = ExtensionStore.getRawState();
              this.notebookListener.reinjectSpecificDID(activeNotebookPanel, did);
            }
          }
        });
      }
    );
  }

  private removeUnfocusedDIDs(attachments: NotebookDIDAttachment[] = []) {
    const shouldNoLongerPoll = this.activePolling.filter(did => !attachments.find(a => a.did === did));
    shouldNoLongerPoll.forEach(did => this.disablePolling(did));
  }

  private processNewAttachments(attachments: NotebookDIDAttachment[] = []) {
    const newlyAdded = attachments.filter(a => !this.activePolling.find(did => did === a.did));
    newlyAdded.forEach(attachment => {
      this.shouldEnablePolling(attachment).then(shouldEnable => {
        if (shouldEnable) {
          this.enablePolling(attachment.did, attachment.type);
        }
      });
    });
  }

  private async shouldEnablePolling(attachment: NotebookDIDAttachment) {
    const { activeInstance } = UIStore.getRawState();

    if (attachment.type === 'file') {
      const didDetails = await actions.getFileDIDDetails(activeInstance.name, attachment.did);
      return didDetails.status === 'REPLICATING';
    } else {
      const didDetails = await actions.getContainerDIDDetails(activeInstance.name, attachment.did);
      return didDetails.find(d => d.status === 'REPLICATING');
    }
  }

  private enablePolling(did: string, type: 'file' | 'container') {
    didPollingManager.requestPolling(did, type, this.pollingRef, false);
    this.activePolling.push(did);
  }

  private disablePolling(did: string) {
    didPollingManager.disablePolling(did, this.pollingRef);
    this.activePolling = this.activePolling.filter(d => d !== did);
  }
}
