import hashlib

from . import db
from .transaction import Transaction


class Block(object):

    def __init__(self, index, transactions, timestamp, nonce, previous_digest, digest=None):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.nonce = nonce
        self.previous_digest = previous_digest
        self.digest = digest or self.hexdigest()

    def __repr__(self):
        return u"Block(index={}, transactions={})".format(self.index, self.transactions)

    def hexdigest(self):
        return hashlib.sha256(u"{}:{}:{}:{}:{}".format(
            self.index, self.transactions, self.timestamp, self.nonce, self.previous_digest)).hexdigest()

    @staticmethod
    def reward(index):
        return 100

    def to_json(self):
        return {
            "index": self.index,
            "transactions": [transaction.to_json() for transaction in self.transactions],
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "previous_digest": self.previous_digest,
            "digest": self.digest,
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            index=data["index"],
            transactions=[Transaction.from_json(transaction) for transaction in data["transactions"]],
            timestamp=data["timestamp"],
            nonce=data["nonce"],
            previous_digest=data["previous_digest"],
            digest=data["digest"],
        )

    @classmethod
    def last(cls):
        try:
            block = cls.from_json(db.block.find().sort('index', -1).limit(1).next())
        except StopIteration:
            db.block.insert_one(GENESIS_BLOCK.to_json())
            return GENESIS_BLOCK

        return block

    @classmethod
    def find(cls, query=None):
        return (cls.from_json(block) for block in db.block.find(query or {}).sort('index', 1))

    @classmethod
    def find_one(cls, query=None):
        return cls.from_json(db.block.find_one(query or {}))


GENESIS_BLOCK = Block(
    index=0,
    transactions=[],
    timestamp=0,
    nonce=0,
    previous_digest=None,
)
