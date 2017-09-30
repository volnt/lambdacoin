import hashlib

import ecdsa

from . import db


class Transaction(object):

    def __init__(self, sender, recipient, amount, timestamp, signature=None, digest=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp
        self.signature = signature
        self.digest = digest or self.hexdigest()

    def __repr__(self):
        return u"Transaction(sender={}, recipient={}, amount={})".format(self.sender, self.recipient, self.amount)

    def hexdigest(self):
        return hashlib.sha256(u"{}:{}:{}:{}".format(
            self.sender, self.recipient, self.amount, self.timestamp)).hexdigest()

    def to_json(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "digest": self.digest,
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            sender=data["sender"],
            recipient=data["recipient"],
            amount=data["amount"],
            signature=data["signature"],
            timestamp=data["timestamp"],
            digest=data["digest"],
        )

    def verify(self):
        public_key = ecdsa.VerifyingKey.from_string(self.sender.decode('hex'))

        return self.digest == self.hexdigest() and public_key.verify(self.signature, self.digest)


class UnconfirmedTransaction(Transaction):

    @classmethod
    def find(cls, query=None):
        return (cls.from_json(transaction)
                for transaction in db.unconfirmed_transaction.find(query or {}).sort('index', 1))
