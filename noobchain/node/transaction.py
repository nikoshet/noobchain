from collections import OrderedDict
from hashlib import sha256
import json


class Transaction:

    _id = 0     # Incremental id for each instance created

    def __init__(self, sender_address, receiver_address, amount, transaction_inputs, transaction_outputs):

        self.sender_address = sender_address                    # Sender's public key
        self.receiver_address = receiver_address                # Receiver's public key
        self.amount = amount                                    # Transfer Amount
        self.transaction_id = Transaction._id                   # Transaction Id
        self.transaction_inputs = transaction_inputs            # Previous Transaction Id
        self.transaction_outputs = transaction_outputs          # {id: (Amount Transferred, Change)}
        self.signature = ''                                     # Proof that sender requested transaction
        self.od = None
        self.current_hash = None

        Transaction._id += 1

    def hash(self):

        if len(self.signature) == '':
            raise Exception(f'Transaction must be signed before attempting any hash')

        # Convert object to ordered dictionary (so it produces same results every time)
        self.od = OrderedDict([
            ('sender_address', self.sender_address),
            ('receiver_address', self.receiver_address),
            ('amount', self.amount),
            ('transaction_id', self.transaction_id),
            ('transaction_inputs', self.transaction_inputs),
            ('transaction_outputs', self.transaction_outputs),
            ('signature', self.signature),
        ])

        self.current_hash = sha256(str(self.od).encode('utf-8')).hexdigest()

        return self

