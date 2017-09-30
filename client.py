from collections import defaultdict

import requests

from . import DataType
from .node import Node


class Client(object):

    def __init__(self, nodes, blockchain=None):
        self.nodes = nodes

    def broadcast(self, data, data_type):
        payload = {
            'type': data_type.value,
            'data': data,
        }

        broadcasted = False

        for node in self.nodes.copy().values():
            try:
                response = requests.post(node.url, json=payload).json()
            except requests.RequestException:
                self.nodes.pop(node)
            else:
                self.BROADCAST_CB[data_type](response)
                broadcasted = True

        return broadcasted

    def update_nodes(self, nodes):
        for node in (Node.from_bson(_node) for _node in nodes):
            if len(self.nodes) < 10:
                self.nodes[node.url] = node
            else:
                break

    BROADCAST_CB = defaultdict(lambda: lambda *args, **kwargs: None, {
        DataType.REQUEST_NODES: update_nodes,
    })
