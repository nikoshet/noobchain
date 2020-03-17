import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4


class Wallet:

    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key
        self.transactions = []

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

    #def verify_transaction(self, public_key, transaction):
    #    return 1
