from collections import defaultdict

from . import DataType, db
from .blockchain import Blockchain
from .client import Client
from .transaction import Transaction
from .block import Block


class Node(Client):

    def __init__(self, url, nodes=None):
        super(Node, self).__init__(nodes or [])
        self.url = url
        self.blockchain = Blockchain()

    def receive(self, payload):
        data_type = DataType(payload["type"])

        if "data" in payload:
            args = (payload["data"], )
        else:
            args = ()

        return self.RECEIVE_CB[data_type](self, *args)

    def to_json(self):
        return {
            "url": self.url,
        }

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def update_blockchain(self, blocks):
        for block in blocks:
            self.blockchain.add_block(Block.from_json(block))

    def fetch_blockchain(self):
        self.broadcast({"since": self.blockchain[-1].index}, DataType.REQUEST_BLOCKCHAIN)

    def receive_transaction(self, transaction):
        transaction = Transaction.from_json(transaction)

        if not transaction.verify():
            return False

        if db.unconfirmed_transaction.find_one({'digest': transaction.digest}):
            return False

        db.unconfirmed_transaction.insert_one(transaction.to_json())
        self.broadcast(transaction.to_json(), DataType.TRANSACTION)

    def receive_block(self, block):
        self.blockchain.add_block(Block.from_json(block))

    RECEIVE_CB = defaultdict(lambda: lambda *args, **kwargs: None, {
        DataType.REQUEST_NODES: lambda self: [node.url for node in self.nodes],
        DataType.REQUEST_BLOCKCHAIN: lambda self, data: [
            block.to_json() for block in self.blockchain.blocks[data.get("since", 0):]],
        DataType.TRANSACTION: receive_transaction,
    })

    BROADCAST_CB = defaultdict(lambda: lambda *args, **kwargs: None, {
        DataType.REQUEST_NODES: Client.update_nodes,
        DataType.REQUEST_BLOCKCHAIN: update_blockchain,
        DataType.BLOCK: receive_block,
    })
