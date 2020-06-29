export const EXTENSION_ID = 'rucio-jupyterlab';
export const METADATA_KEY = 'rucio';
export const COMM_NAME_KERNEL = `${EXTENSION_ID}:kernel`;
export const COMM_NAME_FRONTEND = `${EXTENSION_ID}:frontend`;

export const searchByOptions = [
  { title: 'Datasets or Containers', value: 'datasets' },
  { title: 'Files', value: 'files' }
];

export const authTypeOptions = [
  { label: 'Username & Password', value: 'userpass' },
  { label: 'X.509 User Certificate', value: 'x509' }
];
