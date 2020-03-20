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

    def __init__(self, sender_address, sender_private_key, recipient_address, value):

        self.sender_address = sender_address #To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = 0 #To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = value #το ποσό που θα μεταφερθεί
        self.transaction_id = 0 #το hash του transaction
        self.transaction_inputs = 0 #λίστα από Transaction Input
        self.transaction_outputs = 0 #λίστα από Transaction Output
        self.signature = 0

    def to_dict(self):
        return True

    def sign_transaction(self, private_key):
        """
        Sign transaction with private key
        """

