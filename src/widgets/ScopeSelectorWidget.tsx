import { Widget } from '@lumino/widgets';

export class ScopeSelectorWidget extends Widget {
  /**
   * Create a new scope selector widget.
   */
  constructor() {
    super({ node: createSelectorNode() });
  }

  /**
   * Get the value of the scope selector widget.
   */
  getValue(): string {
    const selector = this.node.querySelector('select') as HTMLSelectElement;
    return selector.value;
  }
}

function createSelectorNode() {
  const body = document.createElement('div');
  const text = document.createElement('label');
  text.textContent = 'Scope';
  body.appendChild(text);

  const selector = document.createElement('select');
  populateScopeSelect(selector);
  body.appendChild(selector);
  return body;
}

function populateScopeSelect(node: HTMLSelectElement): void {
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }

  node.disabled = false;
  node.appendChild(optionForName('TEST_SCOPE'));
}

function optionForName(name: string): HTMLOptionElement {
  const option = document.createElement('option');
  option.text = name;
  option.value = name;
  return option;
}
