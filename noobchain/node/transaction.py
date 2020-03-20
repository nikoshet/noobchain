from collections import OrderedDict
import binascii
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, receiver_address, amount, signature):

        self.sender_address = sender_address        # Sender's public key
        self.receiver_address = receiver_address    # Receiver's public key
        self.amount = amount                        # Transfer Amount
        self.transaction_id = 0                     # Transaction Id
        self.transaction_inputs = 0                 # Previous Transaction Id
        self.transaction_outputs = 0                # id: (Amount Transferred, Change)
        self.signature = signature                  # Proof that sender requested transaction

    def create_transaction(self, ):

        return self

    def sign_transaction(self, private_key):
        self.signature = private_key
        return self



