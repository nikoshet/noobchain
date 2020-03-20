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
        self.signature = None                                   # Proof that sender requested transaction

        Transaction._id += 1

    def to_json(self):

        # Convert object to ordered dictionary (so it produces same results every time)
        _ = {
            'sender_address', self.sender_address,
            'receiver_address', self.receiver_address,
            'amount', self.amount,
            'transaction_id', self.transaction_id,
            'transaction_inputs', self.transaction_inputs,
            'transaction_outputs', self.transaction_outputs,
            'signature', self.signature,
        }

        # Return sha256 of that dictionary
        # return sha256(json.dumps(_, sort_keys=True).digest())

        # Return ordered json
        return json.dumps(_, sort_keys=True)
