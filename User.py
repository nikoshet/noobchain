from Wallet import Wallet
from Crypto.PublicKey import RSA
import re


class User:

    def __init__(self, id, conn):

        # Search database for user (use conn)
        db = []

        if id in db:
            self.name = self.get_name(id=id)
            self.surname = self.get_surname(id=id)
            self.public = self.get_public(id=id)
            self.private = self.get_private(id=id)

        else:
            self.id = id
            self.name = None
            self.surname = None
            self.public, self.private = self.first_time_keys()

        # Go see Wallet class
        self.wallet = Wallet(id)

    def __str__(self):
        return f'------ PRINTING DETAILS FOR USER: [{self.id}] ------' \
               f'\n{self.name} {self.surname}' \
               f'\nPublic key:\n{self.public}' \
               f'\nPrivate key:\n{self.private}'

    def first_time_keys(self):

        # https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html#Crypto.PublicKey.RSA.generate
        # Generate random RSA object
        private = RSA.generate(2048)
        public = private.publickey()

        # exportKey, format param: "PEM" -> string
        #                          "DER" -> binary

        # Remove conventions
        # '-----BEGIN PUBLIC KEY-----\n', '\n-----END PUBLIC KEY-----'
        public = public.exportKey().decode('utf-8')
        public = re.sub('(-----BEGIN PUBLIC KEY-----\\n)|(\\n-----END PUBLIC KEY-----)', '', public)

        # '-----BEGIN RSA PRIVATE KEY-----\n, '\n-----END RSA PRIVATE KEY-----'
        private = private.exportKey().decode('utf-8')
        private = re.sub('(-----BEGIN RSA PRIVATE KEY-----\\n)|(\\n-----END RSA PRIVATE KEY-----)', '', private)

        return public, private

