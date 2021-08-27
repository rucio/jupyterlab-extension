import { Contents } from '@jupyterlab/services';
import { showErrorMessage } from '@jupyterlab/apputils';
import { UIStore } from '../stores/UIStore';
import { actions } from '../utils/Actions';
import { RucioUploadDialog } from '../widgets/RucioUploadDialog';

export default async function uploadFile(files: Contents.IModel[]): Promise<void> {
  const dialog = new RucioUploadDialog(files);
  const result = await dialog.launch();

  const { activeInstance } = UIStore.getRawState();
  if (activeInstance && result.value) {
    const { rse, lifetime, fileScope, datasetScope, datasetName, addToDataset } = result.value;

    if (!rse || !fileScope) {
      showErrorMessage('Upload cancelled', 'Destination RSE and/or scope is not specified.');
      return;
    }

    if (addToDataset) {
      if (!datasetScope || !datasetName) {
        showErrorMessage('Upload cancelled', 'Dataset scope and/or name is not specified.');
        return;
      }
    }

    await actions.uploadFile(activeInstance.name, {
      paths: files.map(s => s.path),
      rse,
      lifetime: lifetime ? parseInt(lifetime) : undefined,
      fileScope,
      datasetScope,
      datasetName,
      addToDataset
    });

    showErrorMessage('Upload is commencing', 'Your files are uploading, you can see the upload status on the Rucio sidebar.');
  }
}
