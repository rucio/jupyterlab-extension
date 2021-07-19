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

import { ExtensionStore } from '../stores/ExtensionStore';
import { UIStore } from '../stores/UIStore';
import { PollingRequesterRef, didPollingManager } from './DIDPollingManager';
import { NotebookDIDAttachment } from '../types';
import { actions } from './Actions';
import { NotebookListener } from './NotebookListener';
import { computeCollectionState } from './Helpers';

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
              if (activeNotebookPanel) {
                this.notebookListener.reinjectSpecificDID(activeNotebookPanel, did);
              }
            }
          }
        });
      }
    );

    // Listen to change in collection status
    UIStore.subscribe(
      s => s.collectionDetails,
      (collectionDetails, state, prevCollectionDetails) => {
        if (!collectionDetails) {
          return;
        }

        const listenedCollectionDetails = Object.keys(collectionDetails)
          .filter(did => this.activeNotebookAttachmentDIDs.includes(did))
          .map(did => ({
            did,
            file: {
              current: collectionDetails[did],
              prev: prevCollectionDetails[did]
            }
          }));

        listenedCollectionDetails.forEach(({ did, file }) => {
          const currentCollectionState = computeCollectionState(file.current);
          if (currentCollectionState === 'REPLICATING') {
            this.enablePolling(did, 'collection');
          } else {
            if (this.activePolling.includes(did)) {
              this.disablePolling(did);
            }
            const prevCollectionState = computeCollectionState(file.prev);
            if (currentCollectionState === 'AVAILABLE' && prevCollectionState === 'REPLICATING') {
              const { activeNotebookPanel } = ExtensionStore.getRawState();
              if (activeNotebookPanel) {
                this.notebookListener.reinjectSpecificDID(activeNotebookPanel, did);
              }
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
    if (!activeInstance) {
      return false;
    }

    if (attachment.type === 'file') {
      const didDetails = await actions.getFileDIDDetails(activeInstance.name, attachment.did);
      return didDetails.status === 'REPLICATING';
    } else {
      const didDetails = await actions.getCollectionDIDDetails(activeInstance.name, attachment.did);
      return didDetails.find(d => d.status === 'REPLICATING');
    }
  }

  private enablePolling(did: string, type: 'file' | 'collection') {
    didPollingManager.requestPolling(did, type, this.pollingRef, false);
    this.activePolling.push(did);
  }

  private disablePolling(did: string) {
    didPollingManager.disablePolling(did, this.pollingRef);
    this.activePolling = this.activePolling.filter(d => d !== did);
  }
}
