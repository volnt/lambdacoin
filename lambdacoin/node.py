from collections import defaultdict

from . import DataType, db
from .blockchain import Blockchain
from .client import Client
from .transaction import Transaction
from .block import Block


class Node(Client):

    def __init__(self, url, nodes=None):
        super(Node, self).__init__(nodes or set())
        self.url = url
        self.blockchain = Blockchain()

    def receive(self, payload):
        data_type = DataType(payload["type"])
        data = payload.get("data", {})

        if data_type == DataType.REQUEST_NODES:
            return list(self.nodes)
        elif data_type == DataType.REQUEST_BLOCKCHAIN:
            return [block.to_json() for block in Block.find({'index': {'$gte': data.get('since', 0)}})]
        elif data_type == DataType.TRANSACTION:
            self.receive_transaction(Transaction.from_json(data))
        elif data_type == DataType.BLOCK:
            if self.blockchain.add_block(Block.from_json(data)):
                return {'status': 'confirmed'}
            return {'status': 'error'}

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def update_blockchain(self, blocks):
        for block in blocks:
            self.blockchain.add_block(Block.from_json(block))

    def fetch_blockchain(self):
        responses = self.broadcast({"since": self.blockchain[-1].index}, DataType.REQUEST_BLOCKCHAIN)

        for response in responses:
            self.update_blockchain(response)

    def receive_transaction(self, transaction):
        if not transaction.verify():
            return False

        if db.unconfirmed_transaction.find_one({'digest': transaction.digest}):
            return False

        db.unconfirmed_transaction.insert_one(transaction.to_json())

        self.broadcast(transaction.to_json(), DataType.TRANSACTION)
