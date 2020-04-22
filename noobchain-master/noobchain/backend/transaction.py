import json
from collections import OrderedDict


class Transaction:

    _id = 0     # Incremental id for each instance created

    def __init__(self, sender_address, receiver_address, amount, transaction_inputs, wallet, ids, genesis=False):

        self.sender_address = sender_address  # Sender's public key
        self.receiver_address = receiver_address  # Receiver's public key
        self.amount = amount  # Transfer Amount
        self.transaction_id = str(ids)+str(Transaction._id)  # Transaction Id
        self.transaction_inputs = transaction_inputs  # Previous Transaction Id
        self.transaction_outputs = []  # {id: (Amount Transferred, Change)}
        self.signature = ''  # Proof that sender requested transaction
        self.wallet = wallet
        self.change = 0
        self.node_id = ids

        if not genesis and self.wallet is not None:  # if we have a none wallet it means we just want the OD constructor
            total_utxo = 0
            for id in self.transaction_inputs:
                total_utxo += wallet.utxos[id]
            self.change = total_utxo - self.amount
            if self.change < 0: self.change = 0
            self.transaction_outputs.append(
                {str(self.node_id) + str(Transaction._id): (self.receiver_address, self.amount)})
            Transaction._id += 1
            self.transaction_outputs.append(
                {str(self.node_id) + str(Transaction._id): (self.receiver_address, self.change)})

        elif self.wallet is not None:
            self.transaction_outputs.append({"id0"+str(Transaction._id): (self.receiver_address, self.amount)})

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
            ('change', self.change),
            ('node_id', self.node_id),
        ])

        return od

    def to_json(self):
        # Convert object to json
        #return json.dumps(self.to_od())
        return json.dumps(self.to_od(), default=str)


    def get_hash(self):
        # This function does not update current_hash, current_hash_obj
        #return sha256(str(self.to_od()).encode('utf-8')).hexdigest()
        return self.get_hash_obj().hexdigest()

    def get_hash_obj(self):
        # Get object instance as it is easier to update while trying new hashes (mining)
        return sha256(str(self.to_od()).encode('utf-8'))
