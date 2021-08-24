import React from 'react';
import { VDomRenderer, VDomModel, Dialog } from '@jupyterlab/apputils';
import { Contents } from '@jupyterlab/services';
import Select from 'react-select';
import RucioLogo from '../components/RucioLogo';
import { UIStore } from '../stores/UIStore';
import { actions } from '../utils/Actions';
import { TextField } from '../components/TextField';

namespace RucioUpload {
  export type DialogValue = {
    rse: string;
    lifetime?: string;
    fileScope: string;
    datasetScope?: string;
    datasetName?: string;
    addToDataset?: boolean;
  };
  export class Model extends VDomModel {
    _rse = '';
    _lifetime = '';
    _scopes: string[] = [];
    _selectedScope = '';
    _selectedDatasetScope = '';
    _datasetName = '';
    _loading = false;
    _addToDataset = false;

    set rse(rse: string) {
      this._rse = rse;
      this.stateChanged.emit(void 0);
    }

    get rse(): string {
      return this._rse;
    }

    set lifetime(lifetime: string) {
      this._lifetime = lifetime;
      this.stateChanged.emit(void 0);
    }

    get lifetime(): string {
      return this._lifetime;
    }

    get scopes(): string[] {
      return this._scopes;
    }

    set scopes(scopes: string[]) {
      this._scopes = scopes;
      this.stateChanged.emit(void 0);
    }

    get selectedScope(): string {
      return this._selectedScope;
    }

    set selectedScope(selectedScope: string) {
      this._selectedScope = selectedScope;
      this.stateChanged.emit(void 0);
    }

    get selectedDatasetScope(): string {
      return this._selectedDatasetScope;
    }

    set selectedDatasetScope(selectedDatasetScope: string) {
      this._selectedDatasetScope = selectedDatasetScope;
      this.stateChanged.emit(void 0);
    }

    get datasetName(): string {
      return this._datasetName;
    }

    set datasetName(datasetName: string) {
      this._datasetName = datasetName;
      this.stateChanged.emit(void 0);
    }

    get loading(): boolean {
      return this._loading;
    }

    set loading(loading: boolean) {
      this._loading = loading;
      this.stateChanged.emit(void 0);
    }

    get addToDataset(): boolean {
      return this._addToDataset;
    }

    set addToDataset(addToDataset: boolean) {
      this._addToDataset = addToDataset;
      this.stateChanged.emit(void 0);
    }
  }

  export class DialogBody extends VDomRenderer<RucioUpload.Model> {
    files: Contents.IModel[];

    constructor(files: Contents.IModel[]) {
      super(new RucioUpload.Model());
      this.files = files;
    }

    onAfterAttach(): void {
      const { activeInstance } = UIStore.getRawState();

      if (activeInstance) {
        this.model.loading = true;
        actions
          .fetchScopes(activeInstance.name)
          .then(result => {
            result.sort((a, b) => a.localeCompare(b));
            this.model.scopes = result;
          })
          .finally(() => (this.model.loading = false));
      }
    }

    render(): React.ReactElement {
      const selectStyles = {
        control: (provided: any, state: any) => ({
          ...provided,
          borderRadius: 0,
          borderColor: 'var(--jp-border-color1)',
          background: 'var(--jp-layout-color1)',
          marginLeft: '1px',
          marginRight: '1px'
        }),
        singleValue: (provided: any, state: any) => ({
          ...provided,
          color: 'var(--jp-ui-font-color1)'
        }),
        menu: (provided: any, state: any) => ({
          ...provided,
          background: 'var(--jp-layout-color1)',
          color: 'var(--jp-ui-font-color1)'
        }),
        menuPortal: (base: any) => ({ ...base, zIndex: 99999 }),
        option: (provided: any, { isFocused, isSelected }: any) => ({
          ...provided,
          background: isFocused ? (isSelected ? provided.background : 'var(--jp-layout-color2)') : provided.background,
          ':active': {
            ...provided[':active'],
            background: isSelected ? provided.background : 'var(--jp-layout-color2)'
          }
        })
      };

      return (
        <div>
          {this.files.length > 1 && <h2 style={{ marginTop: 0 }}>Upload {this.files.length} files to Rucio</h2>}
          {this.files.length === 1 && <h2 style={{ marginTop: 0 }}>Upload {this.files[0].name} to Rucio</h2>}

          <p>Please make sure that the necessary credentials are configured.</p>
          <p>You can see the upload status on the Rucio sidebar.</p>

          <p style={{ marginTop: '16px' }}>Destination RSE Expression:</p>
          <TextField
            value={this.model.rse}
            placeholder="Required"
            onChange={e => (this.model.rse = e.target.value)}
            containerStyle={{ marginTop: '4px', marginBottom: '8px' }}
          />

          <p style={{ marginTop: '16px' }}>Lifetime (in seconds):</p>
          <TextField
            type="number"
            value={this.model.lifetime}
            placeholder="Leave empty for indefinite"
            onChange={e => (this.model.lifetime = e.target.value)}
            containerStyle={{ marginTop: '4px', marginBottom: '8px' }}
          />

          <p style={{ marginTop: '16px' }}>Scope:</p>
          <div style={{ marginTop: '4px', marginBottom: '8px' }}>
            <Select
              isLoading={this.model.loading}
              menuPortalTarget={document.body}
              styles={selectStyles}
              options={this.model.scopes.map(scope => ({ value: scope, label: scope }))}
              defaultValue={{ value: this.model.selectedScope, label: this.model.selectedScope }}
              onChange={(value: any) => (this.model.selectedScope = value.value)}
            />
          </div>

          <React.Fragment>
            <label>
              <input
                type="checkbox"
                checked={this.model.addToDataset}
                onChange={e => (this.model.addToDataset = e.target.checked)}
              />
              Add files to a dataset
            </label>
            {this.model.addToDataset && (
              <div style={{ marginTop: '16px' }}>
                <p>Dataset Scope:</p>
                <div style={{ marginTop: '4px', marginBottom: '8px' }}>
                  <Select
                    isLoading={this.model.loading}
                    menuPortalTarget={document.body}
                    styles={selectStyles}
                    options={this.model.scopes.map(scope => ({ value: scope, label: scope }))}
                    defaultValue={{ value: this.model.selectedDatasetScope, label: this.model.selectedDatasetScope }}
                    onChange={(value: any) => (this.model.selectedDatasetScope = value.value)}
                  />
                </div>
                <p style={{ marginTop: '16px' }}>Dataset Name:</p>
                <TextField
                  value={this.model.datasetName}
                  onChange={e => (this.model.datasetName = e.target.value)}
                  containerStyle={{ marginTop: '4px', marginBottom: '8px' }}
                />
              </div>
            )}
          </React.Fragment>
        </div>
      );
    }

    getValue(): RucioUpload.DialogValue {
      return {
        rse: this.model.rse,
        lifetime: this.model.lifetime,
        fileScope: this.model.selectedScope,
        datasetScope: this.model.selectedDatasetScope,
        datasetName: this.model.datasetName,
        addToDataset: this.model.addToDataset
      };
    }
  }
}

export class RucioUploadDialog extends Dialog<RucioUpload.DialogValue> {
  constructor(files: Contents.IModel[]) {
    super({
      title: <RucioLogo />,
      body: new RucioUpload.DialogBody(files),
      buttons: [
        Dialog.cancelButton(),
        Dialog.okButton({
          label: 'Upload'
        })
      ]
    });
  }

  handleEvent(event: Event): void {
    if (event.type === 'keydown') {
      const keyboardEvent = event as KeyboardEvent;
      if (keyboardEvent.key === 'Enter') {
        return;
      }
    }

    super.handleEvent(event);
  }
}
