

class Transaction:

    def __init__(self, sender_address, receiver_address, amount, transaction_inputs, transaction_outputs):

        self.sender_address = sender_address                    # Sender's public key
        self.receiver_address = receiver_address                # Receiver's public key
        self.amount = amount                                    # Transfer Amount
        self.transaction_id = 0                                 # Transaction Id
        self.transaction_inputs = transaction_inputs            # Previous Transaction Id
        self.transaction_outputs = transaction_outputs          # {id: (Amount Transferred, Change)}
        self.signature = None                                   # Proof that sender requested transaction
