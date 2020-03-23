import json
from collections import OrderedDict


class Transaction:

    _id = 0     # Incremental id for each instance created

    def __init__(self, sender_address, receiver_address, amount, transaction_inputs, transaction_outputs, genesis=False):

        self.sender_address = sender_address                    # Sender's public key
        self.receiver_address = receiver_address                # Receiver's public key
        self.amount = amount                                    # Transfer Amount
        self.transaction_id = Transaction._id                   # Transaction Id
        self.transaction_inputs = transaction_inputs            # Previous Transaction Id
        self.transaction_outputs = transaction_outputs          # {id: (Amount Transferred, Change)}
        self.signature = ''                                     # Proof that sender requested transaction

        if genesis:
            self.signature = 'GENESIS'

        Transaction._id += 1

    def to_od(self):
        # Convert object to ordered dictionary (so it produces same results every time)
        od = OrderedDict([
            ('sender_address', self.sender_address),
            ('receiver_address', self.receiver_address),
            ('amount', self.amount),
            ('transaction_id', self.transaction_id),
            ('transaction_inputs', self.transaction_inputs),
            ('transaction_outputs', self.transaction_outputs),
            ('signature', self.signature),
        ])

        return od

    def to_json(self):
        # Convert object to json
        return json.dumps(self.to_od(), default=str)
