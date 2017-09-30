import datetime

import ecdsa

from . import DataType
from .client import Client
from .transaction import Transaction


class Wallet(Client):

    def __init__(self, private_key=None):
        super(Wallet, self).__init__([])

        self.__private_key = private_key
        self.__public_key = None

        self.generate_key_pair()

    def generate_key_pair(self):
        if self.__private_key:
            self.__private_key = ecdsa.SigningKey.from_string(self.__private_key.decode('hex'), curve=ecdsa.SECP256k1)
        else:
            self.__private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

        self.__public_key = self.__private_key.get_verifying_key()

    @property
    def public_key(self):
        return self.__public_key.to_string().encode('hex')

    @property
    def private_key(self):
        return self.__private_key.to_string().encode('hex')

    def sign(self, transaction):
        transaction.signature = self.__private_key.sign(transaction.digest)

    def send_amount(self, recipient, amount):
        transaction = Transaction(
            sender=self.public_key,
            recipient=recipient,
            amount=amount,
            timestamp=datetime.datetime.utcnow().isoformat())

        self.sign(transaction)

        return self.broadcast(transaction, DataType.TRANSACTION)
