import base64
import json
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
        self.utxos = {}
        self.others_utxos={}
        self.value = self.wallet_balance()

    def wallet_balance(self):
        balance = 0
        for key, value in self.utxos.items():
            print(value)
            balance += value
        return balance

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key

    def get_transactions(self):
        return self.transactions

    def sign_transaction(self, transaction):
        priv_key = RSA.importKey(self.private_key)
        my_sign = PKCS1_v1_5.new(priv_key)
        transaction = transaction.to_od()
        h = SHA.new(json.dumps(transaction, default=str).encode('utf8'))
        return base64.b64encode(my_sign.sign(h)).decode('utf8')
