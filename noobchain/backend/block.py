import time
from collections import OrderedDict
from hashlib import sha256


class Block:

    def __init__(self, index, transactions, nonce, previous_hash):
        self.index = index  # Block Identification
        self.timestamp = time.time()  # Time created
        self.transactions = transactions  # Block's Transactions
        self.nonce = nonce  # Proof of work
        self.previous_hash = previous_hash  # Connecting hash to previous block

        # After successful hashing this should be filled out
        self.current_hash = None  # Current hash
        self.current_hash_obj = None  # Current has as sha256 object to save calculations

    def to_od(self):
        od = OrderedDict([
            ('index', self.index),
            ('timestamp', self.timestamp),
            ('transactions', ([trans.to_od() for trans in self.transactions])),
            ('nonce', self.nonce)
        ])

        return od

    def hash(self, capacity=1, genesis=False):
        if len(self.transactions) < capacity and not genesis:
            raise Exception(f'Trying to hash a block which has {len(self.transactions)} transactions'
                            f', while capacity is {capacity}.')

        od = OrderedDict([
            ('index', self.index),
            ('timestamp', self.timestamp),
            ('transactions', ([trans.to_od() for trans in self.transactions])),
            ('nonce', self.nonce)
        ])

        self.current_hash_obj = sha256(str(od).encode('utf-8'))
        self.current_hash = self.current_hash_obj.hexdigest()

        return self
