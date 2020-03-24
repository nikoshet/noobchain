import time
from threading import Thread
import json
from backend.wallet import Wallet
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import re
import os
import requests
from flask import jsonify
from backend.block import Block
from backend.blockchain import Blockchain
from backend.transaction import Transaction
from collections import OrderedDict
from base64 import b64decode

# from noobchain.main import capacity, difficulty

import binascii

capacity = 5
difficulty = 4


class Node:

    def __init__(self, ip, port, is_bootstrap, ip_of_bootstrap, port_of_bootstrap, no_of_nodes):

        self.ip = ip
        self.port = port
        self.no_of_nodes = no_of_nodes
        self.id = ''
        self.address = self.get_address(self.ip, self.port)

        # Get a public key and a private key with RSA
        self.public, self.private = self.first_time_keys()
        # Create wallet
        self.wallet = self.generate_wallet(self.public, self.private)

        # Here we store information for every node, as its id, its address (ip:port) its public key and its balance
        bootstrap_address = self.get_address(ip_of_bootstrap, port_of_bootstrap)
        self.ring = [{'id': str.join('id', str(0)), 'public_key': self.wallet.public_key, 'address': bootstrap_address}]

        self.bkchain = None
        self.new_block = None
        self.trans = ''
        # Check if node2 is bootstrap
        self.is_bootstrap = is_bootstrap
        if self.is_bootstrap:
            self.id = 'id0'
            self.wallet.utxos["id00"]=500
            #print(self.wallet.utxos)
            self.bkchain = Blockchain(self.ring)
            #self.create_genesis_block()

        else:
            self.wallet.others_utxos["id0"]=[("id00",500)]
            Thread(target=self.register_on_bootstrap).start()
            #self.register_on_bootstrap()

        # self.start(ip, port, ip_of_bootstrap, port_of_bootstrap)

    def __str__(self):
        return f'------ PRINTING DETAILS FOR USER: [{self.ip}] ------' \
               f'\n{self.ip} {self.port}' \
 \
    ### General functions ###

    def register_on_bootstrap(self):
        time.sleep(2)
        message = {'public_key': self.wallet.public_key, 'address': self.address}
        print('Resource:',self.ring[0]['address'] + "/nodes/register")
        req = requests.post(self.ring[0]['address'] + "/nodes/register", json=message)
        if not req.status_code == 200:
            print(req.text)
        else:
            print('Successful registration on bootstrap node')

    # Return address of ip, port
    def get_address(self, ip, port):
        return 'http://' + str(ip) + ':' + str(port)

    # Get a public key and a private key with RSA
    def first_time_keys(self):
        # https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html#Crypto.PublicKey.RSA.generate
        # Generate random RSA object
        gen = RSA.generate(2048)
        private_key = gen.exportKey('PEM').decode()
        public_key = gen.publickey().exportKey('PEM').decode()
        # exportKey, format param: "PEM" -> string
        return public_key, private_key

    # Create a wallet for this node2
    def generate_wallet(self, publ, priv):
        wall = Wallet(publ, priv)
        return wall

    # Create first block of blockchain (for Bootstrap)
    def create_genesis_block(self):
        self.create_new_block(previous_hash=1, nonce=0)
        # self.trans = self.create_transaction(0, self.wallet.public_key, self.no_of_nodes * 100)
        # create genesis transaction
        self.trans = Transaction(sender_address=0, receiver_address=self.address,
                                 amount=500, transaction_inputs='',wallet=self.wallet,id=self.id,genesis=True)

        self.add_transaction_to_block(self.new_block, self.trans)
        # Mine block
        self.bkchain.mine_block(self.new_block)

    def register_node_to_ring(self, message):
        # Add the new node to ring
        # Bootstrap node informs all other nodes and gives the new node an id and 100 NBCs
        node_address = message.get('address')
        public_key = message.get('public_key')
        self.ring.append({'id': str.join('id', str(len(self.ring))), 'public_key': public_key, 'address': node_address})

        #print(self.ring)

        # Broadcast ring to all nodes
        if len(self.ring) == self.no_of_nodes:
            Thread(target=self.broadcast_ring_to_nodes).start()
            Thread(target=self.respond_to_node).start()

    def respond_to_node(self):
        value = 100
        for member in self.ring:
            address = member.get('address')
            if address != self.address:
                #address = member.get('address')
                public_key = member.get('public_key')
                #message = {'sender': self.address, 'receiver': address,
                #          'value': value}
                # req = requests.post(address, jsonify(message))
                self.create_transaction(self.wallet.public_key, public_key, value)
                # if len(self.ring) == self.no_of_nodes:
                #    self.broadcast_ring_to_nodes()

    def broadcast_ring_to_nodes(self):
        for member in self.ring:
            address = member.get('address')
            if address != self.address:
                req = requests.post(address + "/broadcast/ring", json=json.dumps(self.ring))
                if not req.status_code == 200:
                    #print(req.text)
                    print('Error:',req.status_code)
                else:
                    print('Successful registration on bootstrap node from node:', address)

    ### Transaction functions ###

    def create_transaction(self, sender_address, receiver_address, value):
        tmp=0
        trans_input=[]
        print(sender_address)
        for key, available in self.wallet.utxos.items():
            if tmp<value:
                trans_input.append(key)
                tmp+=value
        my_trans = Transaction(sender_address=sender_address, receiver_address=receiver_address,amount=value, transaction_inputs=trans_input,wallet=self.wallet,ids=self.id)
        my_trans.signature = Wallet.sign_transaction(self.wallet, my_trans)
        message = {'transaction': my_trans.to_json()}
        self.broadcast_transaction(message)
        self.verify_signature(dict(my_trans.to_od()),my_trans.signature,self.public)
        return my_trans

    def broadcast_transaction(self, message):
        print('Broadcasting transaction')
        # Post message in ring except me
        for member in self.ring:
            address = member.get('address')
            if address != self.address:
                # Post request
                # send to ring.sender
                req = requests.post(address + "/transactions/create", json=json.dumps(message))# data=jsonify(message))
                if not req.status_code == 200:
                    print('Error:',req.status_code)
                else:
                    print('Success on broadcasting transaction on node:', address)

    def validate_transaction(self, transaction, signature, sender):
        # Use of signature and NBCs balance
        if self.verify_signature(transaction, signature, sender):
            # and # ifxo o utk
            return True
        else:
            print('Error on validating')
            return False

    def verify_signature(self, trans, signature, pub_key):
        sign = PKCS1_v1_5.new(pub_key)
        to_test= OrderedDict([
            ('sender_address', trans["sender_address"]),
            ('receiver_address', trans["receiver_address"]),
            ('amount', trans["amount"]),
            ('transaction_id', trans["transaction_id"]),
            ('transaction_inputs', trans["transaction_inputs"]),
            ('transaction_outputs', trans["transaction_outputs"]),
            ("signature","")])
        to_test = json.dumps(to_test, default=str)
        h = SHA.new(to_test.encode('utf8'))
        public_key = RSA.importKey(pub_key)
        sign_to_test = PKCS1_v1_5.new(public_key)
        if sign_to_test.verify(h,b64decode(trans["signature"])):
            self.update_utxos(trans,self.wallet)
            return True
        return

    def update_utxos(self,trans, portofoli):
        i_got_money = False
        i_got_change = False
        for node in self.ring:
                if node["public_key"]==trans["receiver_address"]:   
                    id_receiver = "id"+str(node["id"])
                if node["public_key"]==trans["sender_address"]:
                    id_sender = "id"+str(node["id"])
        if id_receiver!=self.id:
             try:
                portofoli.others_utxos[id_receiver]
             except:
                portofoli.others_utxos[id_receiver]=[]
        if id_sender!=self.id:
             try:
                 portofoli.others_utxos[id_sender]
             except:
                portofoli.others_utxos[id_sender]=[]

        if trans["receiver_address"]==self.public:
            portofoli.utxos[list(trans["transaction_outputs"][0].keys())[0]]=trans["transaction_outputs"][0][list(trans["transaction_outputs"][0].keys())[0]][1]
            i_got_money = True
        if trans["sender_address"]==self.public:
            for utxos_spend in trans["transaction_inputs"]:
                del portofoli.utxos[utxos_spend]
            if trans["transaction_outputs"][1][list(trans["transaction_outputs"][1].keys())[0]][1]>0:
                portofoli.utxos[list(trans["transaction_outputs"][1].keys())[0]]=trans["transaction_outputs"][1][list(trans["transaction_outputs"][1].keys())[0]][1]
            i_got_change = True
        
        if i_got_money:
            items_to_remove = []
            for item in portofoli.others_utxos[id_sender]:
                if item[0] in trans["transaction_inputs"]:
                    items_to_remove.append(item)
            for item in items_to_remove:
                portofoli.others_utxos[id_sender].remove(item)
            if trans["transaction_outputs"][1][list(trans["transaction_outputs"][1].keys())[0]][1]>0:
                portofoli.others_utxos[id_sender].append((list(trans["transaction_outputs"][1].keys())[0],
                                                                            trans["transaction_outputs"][1][list(trans["transaction_outputs"][1].keys())[0]][1]))
        
        elif i_got_change:
             for node in self.ring:
                if node["public_key"]==trans["receiver_address"]:   
                    id_receiver = "id"+str(node["id"])
                    break
            
             portofoli.others_utxos[id_receiver].append((list(trans["transaction_outputs"][0].keys())[0],trans["transaction_outputs"][0][list(trans["transaction_outputs"][0].keys())[0]][1]))
            
        else:
            portofoli.others_utxos[id_receiver].append((list(trans["transaction_outputs"][0].keys())[0],trans["transaction_outputs"][0][list(trans["transaction_outputs"][0].keys())[0]][1]))
            items_to_remove = []
            for item in portofoli.others_utxos[id_sender]:
                if item[0] in trans["transaction_inputs"]:
                    items_to_remove.append(item)
            for item in items_to_remove:
                portofoli.others_utxos[id_sender].remove(item)
            
            if trans["transaction_outputs"][1][list(trans["transaction_outputs"][1].keys())[0]][1]>0:
                portofoli.others_utxos[id_sender].append((list(trans["transaction_outputs"][1].keys())[0],
                                                                            trans["transaction_outputs"][1][list(trans["transaction_outputs"][1].keys())[0]][1]))
        print(portofoli.wallet_balance())
        print(portofoli.others_utxos)


    def create_new_block(self, previous_hash, nonce):
        new_block_index = len(self.bkchain.blocks)
        self.new_block = Block(new_block_index, [], nonce, previous_hash)
        # return True
        self.bkchain.append(self.new_block)

    def add_transaction_to_block(self, block, transaction):
        # if transaction is for genesis block
        if len(self.bkchain.blocks) == 0:
            self.bkchain.mine_block(block)
        # if enough transactions mine
        if len(self.new_block.transactions) == capacity:
            self.bkchain.mine_block(block)
        # append transaction to block
        else:
            self.new_block.transactions.append(transaction)
        # return True


    def valid_proof(self):
        MINING_DIFFICULTY = difficulty
        return True

    ### Concencus functions ###

    def validate_block(self, chain):
        # Check for the longer chain across all nodes
        for np_of_block in range(1, len(chain)):
            block = chain[np_of_block]
            if not self.valid_proof(block) or block['previous_hash'] != chain[np_of_block - 1].hash:
                return False  # resolve_conflict(block)

    def resolve_conflict(self, block):
        # Resolve correct chain
        # Get blockchain size from all nodes and keep largest
        return True