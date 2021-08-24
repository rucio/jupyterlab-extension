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
    scope: string;
    groupAsDataset?: boolean;
    name?: string;
  };
  export class Model extends VDomModel {
    _scopes: string[] = [];
    _selectedScope = '';
    _name = '';
    _loading = false;
    _groupAsDataset = false;

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

    get name(): string {
      return this._name;
    }

    set name(name: string) {
      this._name = name;
      this.stateChanged.emit(void 0);
    }

    get loading(): boolean {
      return this._loading;
    }

    set loading(loading: boolean) {
      this._loading = loading;
      this.stateChanged.emit(void 0);
    }

    get groupAsDataset(): boolean {
      return this._groupAsDataset;
    }

    set groupAsDataset(groupAsDataset: boolean) {
      this._groupAsDataset = groupAsDataset;
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

          {this.files.length === 1 && (
            <React.Fragment>
              <p style={{ marginTop: '16px' }}>Name:</p>
              <TextField
                value={this.model.name}
                onChange={e => (this.model.name = e.target.value)}
                placeholder={this.files[0].name}
                containerStyle={{ marginTop: '4px', marginBottom: '8px' }}
              />
            </React.Fragment>
          )}
          {this.files.length > 1 && (
            <React.Fragment>
              <label>
                <input
                  type="checkbox"
                  checked={this.model.groupAsDataset}
                  onChange={e => (this.model.groupAsDataset = e.target.checked)}
                />
                Upload files as a dataset
              </label>
              {this.model.groupAsDataset && (
                <>
                  <p style={{ marginTop: '16px' }}>Dataset Name:</p>
                  <TextField
                    value={this.model.name}
                    onChange={e => (this.model.name = e.target.value)}
                    containerStyle={{ marginTop: '4px', marginBottom: '8px' }}
                  />
                </>
              )}
            </React.Fragment>
          )}
        </div>
      );
    }

    getValue(): RucioUpload.DialogValue {
      return {
        scope: this.model.selectedScope,
        groupAsDataset: this.model.groupAsDataset,
        name: this.model.name
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
