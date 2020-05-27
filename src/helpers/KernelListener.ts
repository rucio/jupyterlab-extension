import { Session, SessionManager } from '@jupyterlab/services';

export interface KernelListenerOptions {
  connectListeners?: Array<{ (model: Session.IModel): void }>;
  disconnectListeners?: Array<{ (kernelId: string): void }>;
}

export default class KernelListener {
  sessionManager: SessionManager;
  commIdSet: Set<string>;
  connectListeners: Array<{ (model: Session.IModel): void }>;
  disconnectListeners: Array<{ (modelId: string): void }>;

  constructor(sessionManager: SessionManager, options?: KernelListenerOptions) {
    this.sessionManager = sessionManager;
    this.commIdSet = new Set();

    options = options || {};
    this.connectListeners = options.connectListeners || [];
    this.disconnectListeners = options.disconnectListeners || [];

    sessionManager.runningChanged.connect(this.onRunningChanged, this);
  }

  private onRunningChanged(
    sender: Session.IManager,
    models: Iterable<Session.IModel>
  ): void {
    const arrModels = Array.from(models);
    const newModels = arrModels.filter(x => !this.commIdSet.has(x.id));
    const modelIds = arrModels.map(x => x.id);
    const deletedModels = [...this.commIdSet].filter(
      x => !modelIds.includes(x)
    );

    newModels.forEach(model => {
      this.commIdSet.add(model.id);
      this.connectListeners.forEach(connectListener => connectListener(model));
    });

    deletedModels.forEach(modelId => {
      this.disconnectListeners.forEach(disconnectListener =>
        disconnectListener(modelId)
      );
    });
  }
}
