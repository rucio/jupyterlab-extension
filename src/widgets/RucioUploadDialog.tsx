import React from 'react';
import { VDomRenderer, VDomModel } from '@jupyterlab/apputils';
import { Contents } from '@jupyterlab/services';
import Select from 'react-select';
import RucioLogo from '../components/RucioLogo';
import { UIStore } from '../stores/UIStore';
import { actions } from '../utils/Actions';

namespace RucioUploadDialog {
  export class Model extends VDomModel {
    _scopes: string[] = [];
    _selectedScope = '';
    _loading = false;

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

    get loading(): boolean {
      return this._loading;
    }

    set loading(loading: boolean) {
      this._loading = loading;
      this.stateChanged.emit(void 0);
    }
  }
}

export class RucioUploadDialogWidget extends VDomRenderer<RucioUploadDialog.Model> {
  files: Contents.IModel[];

  constructor(files: Contents.IModel[]) {
    super(new RucioUploadDialog.Model());
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
        <RucioLogo />
        {this.files.length > 1 && <h2>Upload {this.files.length} files to Rucio</h2>}
        {this.files.length === 1 && <h2>Upload {this.files[0].name} to Rucio</h2>}

        <p>Please make sure that the necessary credentials are configured.</p>
        <p>You can see the upload status on the Rucio sidebar.</p>

        <p style={{ marginTop: '16px' }}>Scope:</p>
        <div style={{ marginTop: '4px', marginBottom: '8px' }}>
          <Select
            isLoading={this.model.loading}
            menuPortalTarget={document.body}
            styles={selectStyles}
            options={this.model.scopes.map(scope => ({ value: scope, label: scope }))}
            value={{ value: this.model.selectedScope, label: this.model.selectedScope }}
            onChange={(value: any) => (this.model.selectedScope = value.value)}
          />
        </div>
      </div>
    );
  }

  getValue(): string {
    return this.model.selectedScope;
  }
}
