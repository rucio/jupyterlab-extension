import { createEventBus } from 'ts-event-bus';
import { slot } from 'ts-event-bus';
import { NotebookPanel } from '@jupyterlab/notebook';

const RucioExtensionEvents = {
  activeNotebook: slot<NotebookPanel | undefined>()
};

const EventBus = createEventBus({ events: RucioExtensionEvents });

export default EventBus;
