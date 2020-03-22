import base64

from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
import binascii
from Crypto.PublicKey import RSA

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
        return self.public_key

    def get_private_key(self):
        return self.private_key

    def get_transactions(self):
        return self.transactions

    def sign_transaction(self, transaction):
        #priv_key = RSA.importKey(binascii.unhexlify(self.private_key))
        #priv_key = self.private_key
        priv_key = RSA.importKey(self.private_key)
        my_sign = PKCS1_v1_5.new(priv_key)

        #h = SHA.new(str(transaction)).encode('utf8')
        #h = SHA.new(str(transaction.to_json()).encode('utf8'))#.hexdigest())
        h = SHA.new(transaction.to_json().encode('utf8')) #.hexdigest()  # .hexdigest())
        #h = SHA.new(str(self.to_dict()).encode('utf8'))
        #print(transaction.to_json())
        #print(my_sign.sign(str(transaction.to_od())))
        #return 1
        #return binascii.hexlify(my_sign.sign(h)).decode('ascii')
        #return base64.b64encode(my_sign.sign(h)).decode('utf8')
        #return my_sign.sign(h)
        return base64.b64encode(my_sign.sign(h)).decode('utf8')

        #signature = PKCS1_v1_5.new(private_key).sign(self.transaction_id)
        #return signature