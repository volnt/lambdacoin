import json
from collections import defaultdict
import datetime

from . import DataType
from .blockchain import Blockchain
from .block import Block
from .client import Client
from .transaction import Transaction


class Node(Client):

    def __init__(self, url, public_key, nodes=None):
        super(Node).__init__(self, nodes or [])
        self.url = url
        self.public_key = public_key
        self.blockchain = Blockchain()
        self.unconfirmed_transactions = {}

    def receive(self, payload):
        data_type = DataType(payload["type"])

        if "data" in payload:
            args = (payload["data"], )
        else:
            args = ()

        return json.dumps(self.RECEIVE_CB[data_type](*args))

    def to_json(self):
        return {
            "url": self.url,
        }

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def update_blockchain(self, blocks):
        for block in blocks:
            self.blockchain.add_block(block)

    def fetch_blockchain(self):
        self.broadcast({"since": self.blockchain[-1].index}, DataType.REQUEST_BLOCKCHAIN)

    def mine_block(self):
        transactions, nonce = [], 0

        for transaction in self.unconfirmed_transactions.copy():
            if self.blockchain.find_transaction(transaction):
                self.unconfirmed_transaction.pop(transaction.digest)
            else:
                transactions.append(transaction)

        last_block = self.blockchain.blocks[-1]
        timestamp = datetime.datetime.utcnow().isoformat()

        transactions.append(Transaction(
            sender="0",
            recipient=self.public_key,
            amount=Block.reward(last_block.index + 1),
            timestamp=timestamp,
            signature="0"))

        while True:
            block = Block(
                index=last_block.index - 1,
                transactions=transactions,
                timestamp=timestamp,
                nonce=nonce,
                previous_digest=last_block.digest)

            if block.digest.startswith("0"):
                return block

            nonce += 1


    def receive_transaction(self, transaction):
        transaction = Transaction.from_json(transaction)

        if not transaction.verify():
            return False
        if transaction.digest in self.unconfirmed_transaction:
            return False

        self.unconfirmed_transactions[transaction.digest] = transaction
        self.broadcast(transaction.to_json(), DataType.TRANSACTION)

    RECEIVE_CB = defaultdict(lambda: lambda *args, **kwargs: None, {
        DataType.REQUEST_NODES: lambda self: [node.to_json() for node in self.nodes],
        DataType.REQUEST_BLOCKCHAIN: lambda self, data: self.blockchain.blocks[data["since"]:],
        DataType.TRANSACTION: receive_transaction,
    })

    BROADCAST_CB = defaultdict(lambda: lambda *args, **kwargs: None, {
        DataType.REQUEST_NODES: Client.update_nodes,
        DataType.REQUEST_BLOCKCHAIN: update_blockchain,
    })
