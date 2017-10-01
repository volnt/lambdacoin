import requests

from . import DataType


class Client(object):
    NODES = {
        "http://localhost:6400",
        "http://localhost:6401",
        "http://localhost:6402",
        "http://localhost:6403",
    }

    def __init__(self, nodes):
        self.nodes = nodes or self.NODES

    def broadcast(self, data, data_type):
        payload = {
            'type': data_type.value,
            'data': data,
        }

        responses = []

        for node in self.nodes.copy():
            try:
                response = requests.post(node, json=payload).json()
            except requests.RequestException:
                self.nodes.remove(node)
            else:
                responses.append(response)

        if data_type == DataType.REQUEST_NODES:
            [self.update_nodes(response) for response in responses]

        return responses

    def update_nodes(self, nodes):
        for node in nodes:
            if len(self.nodes) < 10:
                self.nodes.add(node)
            else:
                break
