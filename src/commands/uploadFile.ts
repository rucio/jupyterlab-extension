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
    const { rse, lifetime, fileScope } = result.value;

    if (!rse || !fileScope) {
      showErrorMessage(
        'Upload cancelled',
        'Destination RSE and/or scope is not specified.'
      );
      return;
    }

    try {
      await actions.uploadFile(activeInstance.name, {
        paths: files.map(s => s.path),
        rse,
        lifetime: lifetime ? parseInt(lifetime, 10) : undefined,
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
