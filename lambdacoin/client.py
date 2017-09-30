from collections import defaultdict

import requests

from . import DataType


class Client(object):

    def __init__(self, nodes, blockchain=None):
        self.nodes = nodes

    def broadcast(self, data, data_type):
        payload = {
            'type': data_type.value,
            'data': data,
        }

        responses = []

        for node in self.nodes.copy().values():
            try:
                response = requests.post(node.url, json=payload).json()
            except requests.RequestException:
                self.nodes.remove(node)
            else:
                responses.append(response)

        return responses

    def update_nodes(self, nodes):
        for node in nodes:
            if len(self.nodes) < 10:
                self.nodes.add(node)
            else:
                break

    BROADCAST_CB = defaultdict(lambda: lambda *args, **kwargs: None, {
        DataType.REQUEST_NODES: update_nodes,
    })
