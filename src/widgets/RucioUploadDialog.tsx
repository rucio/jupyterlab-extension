import React from 'react';
import { VDomRenderer, VDomModel, Dialog } from '@jupyterlab/apputils';
import { Contents } from '@jupyterlab/services';
import Select from 'react-select';
import RucioLogo from '../components/RucioLogo';
import { UIStore } from '../stores/UIStore';
import { actions } from '../utils/Actions';
import { TextField } from '../components/TextField';
import { Alert } from '../components/Alert';

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
    _rses: string[] = [];
    _rse = '';
    _lifetime = '';
    _scopes: string[] = [];
    _selectedScope = '';
    _selectedDatasetScope = '';
    _datasetName = '';
    _scopesLoading = false;
    _rsesLoading = false;
    _addToDataset = false;

    get rses(): string[] {
      return this._rses;
    }

    set rses(rses: string[]) {
      this._rses = rses;
      this.stateChanged.emit(void 0);
    }

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

    get scopesLoading(): boolean {
      return this._scopesLoading;
    }

    set scopesLoading(loading: boolean) {
      this._scopesLoading = loading;
      this.stateChanged.emit(void 0);
    }

    get rsesLoading(): boolean {
      return this._rsesLoading;
    }

    set rsesLoading(loading: boolean) {
      this._rsesLoading = loading;
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
        this.model.scopesLoading = true;
        actions
          .fetchScopes(activeInstance.name)
          .then(result => {
            if (result && result.success && Array.isArray(result.scopes)) {
              // Correctly access the 'scopes' property which is a string array
              const scopesArray = result.scopes;

              // Now, sort the array. This works because scopesArray is a string[]
              scopesArray.sort((a, b) => a.localeCompare(b));

              this.model.scopes = scopesArray;
            } else {
              console.error('Failed to fetch scopes:', result);
            }
          })
          .finally(() => (this.model.scopesLoading = false));

        this.model.rsesLoading = true;
        actions
          .fetchRSEs(activeInstance.name, 'availability_write=True')
          .then(result => {
            result.sort((a, b) => a.localeCompare(b));
            this.model.rses = result;
          })
          .finally(() => (this.model.rsesLoading = false));
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
          background: isFocused
            ? isSelected
              ? provided.background
              : 'var(--jp-layout-color2)'
            : provided.background,
          ':active': {
            ...provided[':active'],
            background: isSelected
              ? provided.background
              : 'var(--jp-layout-color2)'
          }
        })
      };

      const { activeAuthType } = UIStore.getRawState();

      return (
        <div>
          {this.files.length > 1 && (
            <h2 style={{ marginTop: 0 }}>
              Upload {this.files.length} files to Rucio
            </h2>
          )}
          {this.files.length === 1 && (
            <h2 style={{ marginTop: 0 }}>
              Upload {this.files[0].name} to Rucio
            </h2>
          )}

          {!(activeAuthType === 'x509' || activeAuthType === 'x509_proxy') && (
            <Alert style={{ marginTop: '8px', marginBottom: '8px' }}>
              You are not using X509 as the authentication method, upload may
              fail if the destination RSE does not support your authentication
              method.
            </Alert>
          )}

          <p style={{ marginTop: '16px' }}>Destination RSE:</p>
          <div style={{ marginTop: '4px', marginBottom: '8px' }}>
            <Select
              isLoading={this.model.rsesLoading}
              menuPortalTarget={document.body}
              styles={selectStyles}
              options={this.model.rses.map(rse => ({ value: rse, label: rse }))}
              defaultValue={{ value: this.model.rse, label: this.model.rse }}
              onChange={(value: any) => (this.model.rse = value.value)}
            />
          </div>

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
              isLoading={this.model.scopesLoading}
              menuPortalTarget={document.body}
              styles={selectStyles}
              options={this.model.scopes.map(scope => ({
                value: scope,
                label: scope
              }))}
              defaultValue={{
                value: this.model.selectedScope,
                label: this.model.selectedScope
              }}
              onChange={(value: any) =>
                (this.model.selectedScope = value.value)
              }
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
                    isLoading={this.model.scopesLoading}
                    menuPortalTarget={document.body}
                    styles={selectStyles}
                    options={this.model.scopes.map(scope => ({
                      value: scope,
                      label: scope
                    }))}
                    defaultValue={{
                      value: this.model.selectedDatasetScope,
                      label: this.model.selectedDatasetScope
                    }}
                    onChange={(value: any) =>
                      (this.model.selectedDatasetScope = value.value)
                    }
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
