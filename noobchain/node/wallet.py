
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
import binascii


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

    def sign_transaction(self, transaction):
        #private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        private_key = self.private_key
        sign = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(transaction)).encode('utf8')
        #h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(sign.sign(h)).decode('ascii')

    # def verify_transaction(self, public_key, transaction):
    #    return 1
