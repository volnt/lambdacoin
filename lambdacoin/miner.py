import datetime

from . import DataType, db
from .block import Block
from .blockchain import Blockchain
from .client import Client
from .transaction import Transaction, UnconfirmedTransaction


class Miner(Client):

    def __init__(self, public_key):
        self.public_key = public_key
        self.blockchain = Blockchain()

    def mine_block(self):
        transactions, nonce = [], 0

        for transaction in UnconfirmedTransaction.find():
            if self.blockchain.find_transaction(transaction):
                db.unconfirmed_transaction.delete_one({'digest': transaction.digest})
            else:
                transactions.append(transaction)

        last_block = Block.last()
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

            if last_block.digest != Block.last().digest:
                return

    def mine(self):
        block = None

        while not block:
            block = self.mine_block()

        self.broadcast(block.to_json(), DataType.BLOCK)
