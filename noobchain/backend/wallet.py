import base64
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
import binascii
from Crypto.PublicKey import RSA
from collections import OrderedDict
from hashlib import sha256
import json


class Wallet:

    def __init__(self, public_key, private_key, transactions=None, utxos=None, others_utxos=None, value=None):
        #self.id = node_id
        self.public_key = public_key
        self.private_key = private_key

        if transactions is None:
            transactions = []

        self.transactions = transactions

        if utxos is None:
            utxos = {}

        self.utxos = utxos

        if others_utxos is None:
            others_utxos = {}

        self.others_utxos = others_utxos

        if value is None:
            value = self.wallet_balance()

        self.value = value

    def wallet_balance(self):
        balance = 0
        for key, value in self.utxos.items():
            balance += value
        print('Balance:', balance, 'NBC coins')
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

    def to_od(self):
        od = OrderedDict([
            ('public_key', self.public_key),
            ('private_key', self.private_key),
            ('transactions', ([trans.to_od() for trans in self.transactions])),
            ('utxos', self.utxos),
            ('others_utxos', self.others_utxos),
            ('value', self.value)
        ])
        return od

    def to_json(self):
        # Convert object to json
        return json.dumps(self.to_od(), default=str)
