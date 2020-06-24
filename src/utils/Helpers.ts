import { FileDIDDetails, ContainerStatus } from '../types';

export const computeContainerState = (files: FileDIDDetails[]): ContainerStatus | false => {
  if (!files) {
    return false;
  }

  if (files.length === 0) {
    return 'AVAILABLE';
  }

  const available = files.find(file => file.status === 'OK');
  const notAvailable = files.find(file => file.status === 'NOT_AVAILABLE');
  const replicating = files.find(file => file.status === 'REPLICATING');
  const stuck = files.find(file => file.status === 'STUCK');

  if (replicating) {
    return 'REPLICATING';
  }

  if (stuck) {
    return 'STUCK';
  }

  if (!available) {
    return 'NOT_AVAILABLE';
  }

  if (notAvailable) {
    return 'PARTIALLY_AVAILABLE';
  }

  return 'AVAILABLE';
};

export const checkVariableNameValid = (variableName: string): boolean => {
  // Empty string
  if (!variableName) {
    return false;
  }

  // Includes non-alphanumeric and non-underscore characters
  if (!variableName.match(/^[a-zA-Z0-9_]*$/)) {
    return false;
  }

  // Begins with number
  if (!isNaN(parseInt(variableName.charAt(0)))) {
    return false;
  }

  return true;
};

export const toHumanReadableSize = (bytes: number): string => {
  if (bytes / (1024 * 1024 * 1024) >= 1) {
    const sizeInGb = bytes / (1024 * 1024 * 1024);
    return `${Math.round(sizeInGb * 100) / 100}GiB`;
  } else if (bytes / (1024 * 1024) >= 1) {
    const sizeInMb = bytes / (1024 * 1024);
    return `${Math.round(sizeInMb * 100) / 100}MiB`;
  } else if (bytes / 1024 >= 1) {
    const sizeInKb = bytes / 1024;
    return `${Math.round(sizeInKb * 100) / 100}KiB`;
  } else {
    return `${bytes}B`;
  }
};
