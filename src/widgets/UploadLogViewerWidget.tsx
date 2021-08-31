import React from 'react';
import { VDomRenderer, VDomModel, MainAreaWidget } from '@jupyterlab/apputils';
import { fileUploadIcon } from '@jupyterlab/ui-components';
import { UIStore } from '../stores/UIStore';
import { actions } from '../utils/Actions';
import { EXTENSION_ID } from '../const';

namespace UploadLogViewer {
  export class Model extends VDomModel {
    _log = '';

    get log(): string {
      return this._log;
    }

    set log(log: string) {
      this._log = log;
      this.stateChanged.emit(void 0);
    }
  }

  export class WidgetBody extends VDomRenderer<UploadLogViewer.Model> {
    uploadJobId: string;

    constructor(uploadJobId: string) {
      super(new UploadLogViewer.Model());
      this.uploadJobId = uploadJobId;
      this.title.icon = fileUploadIcon;
      this.id = `${EXTENSION_ID}:upload-log-viewer-${uploadJobId}`;
      this.title.label = `Upload Job #${uploadJobId}`;
      this.title.closable = true;
    }

    onAfterAttach(): void {
      const { activeInstance } = UIStore.getRawState();

      if (activeInstance) {
        actions
          .fetchUploadJobLog(activeInstance.name, this.uploadJobId)
          .then(result => {
            this.model.log = result.text;
          })
          .catch(e => {
            console.log(e);
            this.model.log = 'Error reading upload job log.';
          });
      }
    }

    render(): React.ReactElement {
      return (
        <div style={{ height: '100%', overflow: 'auto', flex: 1 }}>
          <div style={{ padding: '8px', color: 'var(--jp-ui-font-color0)' }}>
            <code style={{ whiteSpace: 'pre' }}>{this.model.log}</code>
          </div>
        </div>
      );
    }
  }
}

export class UploadLogViewerWidget extends MainAreaWidget {
  constructor(uploadJobId: string) {
    super({ content: new UploadLogViewer.WidgetBody(uploadJobId) });
  }
}
