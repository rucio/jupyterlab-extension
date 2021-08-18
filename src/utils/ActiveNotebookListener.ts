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
import { ExtensionStore, ExtensionState } from '../stores/ExtensionStore';
import { NotebookDIDAttachment } from '../types';
import { METADATA_ATTACHMENTS_KEY } from '../const';
import { ReadonlyPartialJSONArray } from '@lumino/coreutils';
import { SessionManager } from '@jupyterlab/services';
import { NotebookListener } from './NotebookListener';

export interface NotebookListenerOptions {
  labShell: ILabShell;
  notebookTracker: INotebookTracker;
  sessionManager: SessionManager;
  notebookListener: NotebookListener;
}

export class ActiveNotebookListener {
  options: NotebookListenerOptions;

  constructor(options: NotebookListenerOptions) {
    this.options = options;
    this.setup();
  }

  private setup(): void {
    const { labShell } = this.options;

    ExtensionStore.subscribe(
      s => s.activeNotebookAttachment,
      (attachments, state) => {
        if (attachments) {
          this.onNotebookAttachmentChanged(attachments, state);
        }
      }
    );

    labShell.currentChanged.connect(this.onCurrentTabChanged, this);
  }

  private onNotebookAttachmentChanged(attachments: NotebookDIDAttachment[], state: ExtensionState) {
    const { activeNotebookPanel } = state;

    if (!attachments || !activeNotebookPanel) {
      return;
    }

    this.setJupyterNotebookFileRucioMetadata(attachments, state);

    if (activeNotebookPanel.sessionContext.session?.kernel) {
      activeNotebookPanel.sessionContext.ready.then(() => {
        const { notebookListener } = this.options;
        notebookListener.injectUninjected(activeNotebookPanel);
      });
    }
  }

  private setJupyterNotebookFileRucioMetadata(attachments: NotebookDIDAttachment[], state: ExtensionState) {
    const metadata = state.activeNotebookPanel?.model?.metadata;
    if (!metadata) {
      return;
    }

    const current = metadata.get(METADATA_ATTACHMENTS_KEY) as ReadonlyArray<any>;
    const rucioDidAttachments = attachments as ReadonlyArray<any>;

    if (current !== rucioDidAttachments) {
      if (rucioDidAttachments.length === 0) {
        if (current) {
          metadata.delete(METADATA_ATTACHMENTS_KEY);
        }
      } else {
        metadata.set(METADATA_ATTACHMENTS_KEY, rucioDidAttachments as ReadonlyPartialJSONArray);
      }
    }
  }

  private onCurrentTabChanged() {
    if (!this.isCurrentTabANotebook()) {
      this.setActiveNotebook(undefined);
      this.setActiveNotebookAttachments(undefined);
      return;
    }

    const { notebookTracker } = this.options;
    const nbWidget = notebookTracker.currentWidget;

    if (!nbWidget) {
      return;
    }

    nbWidget.revealed.then(() => {
      this.setActiveNotebook(nbWidget);
      const rucioDidAttachments = nbWidget.model?.metadata.get(METADATA_ATTACHMENTS_KEY);
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

  private setActiveNotebook(activeNotebook?: NotebookPanel) {
    ExtensionStore.update(s => {
      s.activeNotebookPanel = activeNotebook as any;
    });
  }

  private setActiveNotebookAttachments(attachments?: NotebookDIDAttachment[]) {
    ExtensionStore.update(s => {
      s.activeNotebookAttachment = attachments;
    });
  }
}
