import hashlib


class Block(object):

    def __init__(self, index, transactions, timestamp, nonce, previous_digest, digest):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.nonce = nonce
        self.previous_digest = previous_digest
        self.digest = digest or self.hexdigest()

    def hexdigest(self):
        return hashlib.sha256(u"{}:{}:{}:{}:{}:{}".format(
            self.index, self.transactions, self.timestamp, self.nonce, self.previous_digest)).hexdigest()

    @staticmethod
    def reward(index):
        return 100


GENESIS_BLOCK = Block(
    index=0,
    transactions=[],
    timestamp=0,
    nonce=0,
    previous_digest=None,
)
