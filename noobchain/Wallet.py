

class Wallet:

    def __init__(self, public_key, private_key):
        #self.id = node_id
        self.public_key = public_key
        self.private_key = private_key
        self.transactions = []
        self.value = 0

    def wallet_balance(self):
        for trans in self.transactions:
            # add UTXOS where receiver is this wallet
            return 0

    def get_public_key(self):
        return 1

    def get_private_key(self):
        return 1

    # def get_address(self):
    #	return self.address

    def get_transactions(self):
        return self.transactions

    def sign_transaction(self, private_key, transaction):
        return 1

    # def verify_transaction(self, public_key, transaction):
    #    return 1
