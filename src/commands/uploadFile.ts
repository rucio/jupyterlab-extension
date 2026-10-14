import { Contents } from '@jupyterlab/services';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { UIStore } from '../stores/UIStore';
import { actions } from '../utils/Actions';
import { RucioUploadDialog } from '../widgets/RucioUploadDialog';

export default async function uploadFile(
  files: Contents.IModel[]
): Promise<void> {
  const dialog = new RucioUploadDialog(files);
  const result = await dialog.launch();

  const { activeInstance } = UIStore.getRawState();
  if (activeInstance && result.value) {
    const {
      rse,
      lifetime,
      fileScope,
      addToDataset,
      datasetScope,
      datasetName
    } = result.value;

    if (!rse || !fileScope) {
      showErrorMessage(
        'Upload cancelled',
        'Destination RSE and/or file scope is not specified.'
      );
      return;
    }

    const normalizedDatasetScope = datasetScope?.trim();
    const normalizedDatasetName = datasetName?.trim();
    const normalizedLifetime = lifetime?.trim();

    if (addToDataset && (!normalizedDatasetScope || !normalizedDatasetName)) {
      showErrorMessage(
        'Upload cancelled',
        'Dataset scope and dataset name are required when adding files to a dataset.'
      );
      return;
    }

    if (
      !addToDataset &&
      normalizedLifetime &&
      !/^\d+$/.test(normalizedLifetime)
    ) {
      showErrorMessage(
        'Upload cancelled',
        'Lifetime must be a non-negative integer in seconds.'
      );
      return;
    }

    try {
      await actions.uploadFile(activeInstance.name, {
        paths: files.map(s => s.path),
        rse,
        ...(addToDataset
          ? {
              datasetScope: normalizedDatasetScope,
              datasetName: normalizedDatasetName
            }
          : {
              lifetime: normalizedLifetime
                ? Number(normalizedLifetime)
                : undefined
            }),
        fileScope
      });

      await showDialog({
        title: 'Upload started',
        body: 'Your files are uploading. Check the Rucio sidebar for status.',
        buttons: [Dialog.okButton()]
      });
    } catch (error) {
      showErrorMessage('Upload failed', error as Error);
    }
  }
}
