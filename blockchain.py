from collections import defaultdict

from .block import GENESIS_BLOCK


class Blockchain(object):

    def __init__(self):
        self.blocks = [GENESIS_BLOCK]

    def add_block(self, block):
        if self.is_valid(block) and block.index == self.blocks[-1].index + 1:
            self.blocks.append(block)

    def is_valid(self, block):
        if block.index == 0 and block.digest != GENESIS_BLOCK.digest:
            return False

        if block.index == 0:
            return True

        if not block.digest.startswith("0"):
            return False

        if block.digest != block.hexdigest():
            return False

        if self.blocks[block.index - 1].digest != block.previous_digest:
            return False

        transactions = defaultdict(int)
        for transaction in block.transactions[:-1]:
            if not transaction.verify():
                return False
            if self.find_transaction(transaction):
                return False

            transactions[transaction.sender] -= transaction.amount
            transactions[transaction.recipient] += transaction.amount

        for public_key, amount in transactions.iteritems():
            if self.get_balance(public_key) + amount < 0:
                return False

        reward = block.transactions[-1]

        if reward.amount != block.reward or reward.sender != "0":
            return False

        return True

    def find_transaction(self, transaction):
        for block in self.blocks:
            for transaction in block.transactions:
                if transaction.digest == transaction.digest:
                    return block

    def get_balance(self, public_key):
        balance = 0
        for block in self.blocks:
            for transaction in block.transactions:
                if transaction.sender == public_key:
                    balance -= transaction.amount
                elif transaction.recipient == public_key:
                    balance += transaction.amount
        return balance
