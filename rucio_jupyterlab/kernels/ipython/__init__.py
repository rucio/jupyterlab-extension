# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

from ipykernel.comm import Comm
from .types import MultipleItemDID, SingleItemDID

COMM_NAME = 'rucio-jupyterlab'
KERNEL_COMM_NAME = COMM_NAME + ':kernel'
FRONTEND_COMM_NAME = COMM_NAME + ':frontend'


class RucioDIDAttachmentConnector:
    def __init__(self, ipython):
        self.ipython = ipython

    def register_outgoing_comm(self):
        self.send_comm = Comm(target_name=FRONTEND_COMM_NAME)

        @self.send_comm.on_msg
        def _recv(msg):
            self.handle_comm_message(msg)

    def register_comm(self):
        self.ipython.kernel.comm_manager.register_target(KERNEL_COMM_NAME, self.target_func)

    def target_func(self, comm, msg):
        self.comm = comm

        @self.comm.on_msg
        def _recv(msg):
            self.handle_comm_message(msg)

    def handle_comm_message(self, msg):
        data = msg['content']['data']
        action = data['action']

        if action == 'inject':
            dids = data['dids']
            self.inject_dids(dids)

    def inject_dids(self, dids):
        injected_variable_names = []
        for did in dids:
            did_type = did.get('type')
            variable_name = did.get('variableName')
            files = did.get('files')
            if did_type == 'collection':
                did_available = did.get('didAvailable', True)
                items = [SingleItemDID(path=x.get('path'), pfn=x.get('pfn')) for x in files]
                injected_obj = MultipleItemDID(items=items, did_available=did_available)
            else:
                if files is None:
                    injected_obj = SingleItemDID(path=None)
                else:
                    item = files[0]
                    injected_obj = SingleItemDID(path=item.get('path'), pfn=item.get('pfn'))

            injected_variable_names.append(variable_name)
            self.ipython.push({variable_name: injected_obj})

        self.send_ack_inject(injected_variable_names)

    def send_ack_inject(self, injected_variable_names):
        self.send_comm.send(data={'action': 'ack-inject', 'variable_names': injected_variable_names})

    def send_injection_request(self):
        self.send_comm.send(data={'action': 'request-inject'})


def load_ipython_extension(ipython):
    connector = RucioDIDAttachmentConnector(ipython)
    connector.register_comm()
    connector.register_outgoing_comm()

    def resolve_dids():
        connector.send_injection_request()

    ipython.push({'resolve_dids': resolve_dids})
