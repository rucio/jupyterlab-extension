import { ExtensionStore } from '../stores/ExtensionStore';
import { UIStore } from '../stores/UIStore';
import { PollingRequesterRef, didPollingManager } from './DIDPollingManager';
import { NotebookDIDAttachment } from '../types';
import { actions } from './Actions';

export class NotebookPollingListener {
  pollingRef: PollingRequesterRef;
  activePolling: string[] = [];

  constructor() {
    this.pollingRef = new PollingRequesterRef();

    // Listen to change in attachments
    ExtensionStore.subscribe(
      s => s.activeNotebookAttachment,
      attachments => {
        this.removeUnfocusedDIDs(attachments);
        this.processNewAttachments(attachments);
      }
    );

    // Listen to change in file status
    UIStore.subscribe(
      s => s.fileDetails,
      fileDetails => {
        if (!fileDetails) {
          return;
        }

        const listenedFileDetails = Object.keys(fileDetails)
          .filter(did => this.activePolling.includes(did))
          .map(did => ({ did, file: fileDetails[did] }));

        listenedFileDetails.forEach(({ did, file }) => {
          if (file.status === 'REPLICATING') {
            this.enablePolling(did, 'file');
          } else {
            this.disablePolling(did);
          }
        });
      }
    );

    // Listen to change in container status
    UIStore.subscribe(
      s => s.containerDetails,
      containerDetails => {
        if (!containerDetails) {
          return;
        }

        const listenedContainerDetails = Object.keys(containerDetails)
          .filter(did => this.activePolling.includes(did))
          .map(did => ({ did, file: containerDetails[did] }));

        listenedContainerDetails.forEach(({ did, file }) => {
          if (file.find(d => d.status === 'REPLICATING')) {
            this.enablePolling(did, 'container');
          } else {
            this.disablePolling(did);
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
