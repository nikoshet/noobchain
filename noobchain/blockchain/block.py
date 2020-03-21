import time
from collections import OrderedDict
from hashlib import sha256


class Block:
    _id = 0  # Incremental id for each instance created

    def __init__(self, transactions, nonce, previous_hash):
        self.index = Block._id  # Block Identification
        self.timestamp = time.time()  # Time created
        self.transactions = transactions  # Block's Transactions
        self.nonce = nonce  # Proof of work
        self.previous_hash = previous_hash  # Connecting hash to previous block

        # After successful hashing this should be filled out
        self.current_hash = None  # Current hash
        self.current_hash_obj = None  # Current has as sha256 object to save calculations
        self.od = None

        Block._id += 1

    def hash(self, capacity=2, genesis=False):
        if len(self.transactions) < capacity and not genesis:
            raise Exception(f'Trying to hash a block which has {len(self.transactions)} transactions'
                            f', while capacity is {capacity}.')

        self.od = OrderedDict([
            ('index', self.index),
            ('timestamp', self.timestamp),
            # Use hash of each transaction, instead of it's dictionary
            ('transactions', ([trans.current_hash for trans in self.transactions])),
            ('nonce', self.nonce),
            ('current_hash', self.current_hash),
        ])

        self.current_hash_obj = sha256(str(self.od).encode('utf-8'))
        self.current_hash = self.current_hash_obj.hexdigest()

        return self
