import { Contents } from '@jupyterlab/services';
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
      return;
    }

    actions
      .uploadFile(activeInstance.name, {
        paths: files.map(s => s.path),
        rse,
        lifetime: lifetime ? parseInt(lifetime) : undefined,
        fileScope,
        datasetScope,
        datasetName,
        addToDataset
      })
      .then(r => console.log(r));
  }
}
