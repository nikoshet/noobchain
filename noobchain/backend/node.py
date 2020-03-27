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
from copy import deepcopy

#from main import capacity, difficulty

import binascii

#capacity = 1
#difficulty = 4

class Node:

    def __init__(self, ip, port, is_bootstrap, ip_of_bootstrap, port_of_bootstrap, no_of_nodes, capacity, difficulty):

        self.ip = ip
        self.port = port
        self.no_of_nodes = no_of_nodes
        self.id = ''
        self.address = self.get_address(self.ip, self.port)
        self.pending_transactions=[]

        # Get a public key and a private key with RSA
        self.public, self.private = self.first_time_keys()
        # Create wallet
        self.wallet = self.generate_wallet(self.public, self.private)

        # Here we store information for every node, as its id, its address (ip:port) its public key and its balance
        bootstrap_address = self.get_address(ip_of_bootstrap, port_of_bootstrap)
        self.ring = [{'id': str.join('id', str(0)), 'public_key': self.wallet.public_key, 'address': bootstrap_address}]

        self.blockchain = None
        self.new_block = None
        self.trans = ''
        self.mining=True

        self.capacity = capacity
        self.difficulty = difficulty

        # Check if node is bootstrap
        self.is_bootstrap = is_bootstrap

        if self.is_bootstrap:
            self.id = 'id0'
            self.wallet.utxos["id00"]=500
            self.blockchain = Blockchain(self.ring,self.id)

        else:
            self.wallet.others_utxos["id0"] = [("id00", 500)]

            # Not sure about the runtime of this thread, uncomment
            Thread(target=self.register_on_bootstrap).start()
            #self.register_on_bootstrap()



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
        self.blockchain.mine_block(self.new_block)

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
            #self.broadcast_ring_to_nodes()
            #self.respond_to_node()

    def respond_to_node(self):
        value = 100
        i = 1
        for member in self.ring:
            address = member.get('address')
            if address != self.address:
                print(i)
                i += 1
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
        #lastly broadcast it to ourselves because we want to have the same json, just to be sure
        for member in self.ring:
            address = member.get('address')
            if address == self.address:
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
        for key, available in self.wallet.utxos.items():
            if tmp<value:
                trans_input.append(key)
                tmp+=available
        # If we don't have the money we can't create the transaction
        # if tmp<value:
        #   print("HEY DON'T CHEAT I HAVE ENOUGH BUGS ALREADY")
        #  return False
        my_trans = Transaction(sender_address=sender_address, receiver_address=receiver_address,amount=value, transaction_inputs=trans_input,wallet=self.wallet,ids=self.id)
        my_trans.signature = Wallet.sign_transaction(self.wallet, my_trans)
        message = {'transaction': my_trans.to_json()}
        self.broadcast_transaction(message)
        return my_trans

    def broadcast_transaction(self, message):
        print('Broadcasting transaction')
        # Post message in ring except me
        for member in self.ring:
            address = member.get('address')
            if address != self.address:
                # Post request
                # send to ring.sender
                req = requests.post(address + "/broadcast/transaction", json=json.dumps(message))# data=jsonify(message))
                if not req.status_code == 200:
                    print('Error:',req.status_code)
                else:
                    print('Success on broadcasting transaction on node:', address)
        #also broadcast it to ourselves because we have the object and we want the json, we are leveling everything between the boot and the nodes
        for member in self.ring:
            address = member.get('address')
            if address == self.address:
                # Post request
                # send to ring.sender
                req = requests.post(address + "/broadcast/transaction", json=json.dumps(message))# data=jsonify(message))
                if not req.status_code == 200:
                    print('Error:',req.status_code)
                else:
                    print('Success on broadcasting transaction on node:', address)

    def validate_transaction(self, transaction, signature, sender):
        #parse the transaction to ordered dictionary
        transaction= OrderedDict([
            ('sender_address', transaction["sender_address"]),
            ('receiver_address', transaction["receiver_address"]),
            ('amount', transaction["amount"]),
            ('transaction_id', transaction["transaction_id"]),
            ('transaction_inputs', transaction["transaction_inputs"]),
            ('transaction_outputs', transaction["transaction_outputs"]),
            ("signature",transaction["signature"]),
            ("change",transaction["change"]),
            ("node_id",transaction["node_id"])])
        #if I am not the bootstrap I dont have a blockchain
        if self.blockchain == None: 
            self.blockchain = Blockchain(self.ring, self.id)
        #check signature and value of the transaction
        if self.verify_value(transaction) and self.verify_signature(transaction, sender):
            # if everything is good change the UTXOS
            self.update_utxos(transaction, self.wallet)
            #add to list of transactions
            self.pending_transactions.append(transaction)
            #if I have reached my capacity it's time to create new block and mine it
            if len(self.pending_transactions)>=self.capacity:
                self.mine_new_block()
            return True
        else:
            print('Error on validating')
            return False


    def mine_new_block(self):
        #create the new block and start mining it
        self.mining = True
        new_block_index = self.blockchain.blocks[-1].index + 1
        previous_hash = self.blockchain.blocks[new_block_index-1].current_hash
        nonce=0
        self.new_block = Block(new_block_index, self.pending_transactions[:self.capacity], nonce, previous_hash)
        mine_thread = Thread(target = self.blockchain.mine_block, args =(self.new_block, self.difficulty, lambda : self.mining))#nice lambda trick its a way to kill the mining thread
        mine_thread.start()
        return

    def verify_value(self,trans):
        #check that the utxos of the sender are enough to create this transaction and he is not cheating
        id_sender = trans["node_id"]
        amount = trans["amount"]
        to_be_checked = trans["transaction_inputs"]
        available_money = 0
        if id_sender==self.id:
            unspent_transactions = [(k, v) for k, v in self.wallet.utxos.items()] 
        else:
            unspent_transactions = self.wallet.others_utxos[id_sender]
        for unspent in unspent_transactions:
            if unspent[0] in to_be_checked:
                available_money+=unspent[1]
        if available_money>=amount:
            return True
        else:
            print(amount)
            print("Not Enough UTXOS")
            print(available_money)
            return False

    def verify_signature(self, trans, pub_key):
        #verify the signature of the sender
        sign = PKCS1_v1_5.new(pub_key)
        #transform the json/dictionary to ordered dictionary format so that we have the same hash
        to_test= deepcopy(trans)
        to_test["signature"] = ""
        to_test = json.dumps(to_test, default=str)
        h = SHA.new(to_test.encode('utf8'))
        public_key = RSA.importKey(pub_key)
        sign_to_test = PKCS1_v1_5.new(public_key)
        if sign_to_test.verify(h,b64decode(trans["signature"])):
            return True
        print("Wrong signature")
        return False

    def update_utxos(self,trans, portofoli):
        #state variables to check wheter I was involved in the transaction
        i_got_money = False
        i_got_change = False
        #find the sender and the receiver id from the ring
        for node in self.ring:
                if node["public_key"]==trans["receiver_address"]:   
                    id_receiver = "id"+str(node["id"])
                if node["public_key"]==trans["sender_address"]:
                    id_sender = "id"+str(node["id"])
        #check wheter I have created a key in the dictionary for the ones in the current transaction
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

        #If I was the one getting money upgrade my utxos
        if trans["receiver_address"]==self.public:
            portofoli.utxos[list(trans["transaction_outputs"][0].keys())[0]]=trans["transaction_outputs"][0][list(trans["transaction_outputs"][0].keys())[0]][1]
            i_got_money = True
        #If I was the one sending money delete the utxos that I used from wallet and if I am expecting change create a new utxo with the change    
        if trans["sender_address"]==self.public:
            for utxos_spend in trans["transaction_inputs"]:
                del portofoli.utxos[utxos_spend]
            if trans["transaction_outputs"][1][list(trans["transaction_outputs"][1].keys())[0]][1]>0:
                portofoli.utxos[list(trans["transaction_outputs"][1].keys())[0]]=trans["transaction_outputs"][1][list(trans["transaction_outputs"][1].keys())[0]][1]
            i_got_change = True
        #Again if I was the one that got money I have to fix the utxos of the sender 
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
        
        #if I get change, i.e. I spend more utxos than the value I wanted to send, I have to upgrade my utxos
        elif i_got_change:
             for node in self.ring:
                if node["public_key"]==trans["receiver_address"]:   
                    id_receiver = "id"+str(node["id"])
                    break
            
             portofoli.others_utxos[id_receiver].append((list(trans["transaction_outputs"][0].keys())[0],trans["transaction_outputs"][0][list(trans["transaction_outputs"][0].keys())[0]][1]))
        #the last case is that I did not participate in this transaction so I have to upgrade the utxos of the sender and the receiver, mind that for the sender I must delete the inputs of the transaction and create new utxo if he got change    
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
        return


    def create_new_block(self, previous_hash, nonce):
        new_block_index = len(self.blockchain.blocks)
        self.new_block = Block(new_block_index, [], nonce, previous_hash)
        # return True
        self.blockchain.append(self.new_block)

    def add_transaction_to_block(self, block, transaction):
        # if transaction is for genesis block
        if len(self.blockchain.blocks) == 0:
            self.blockchain.mine_block(block)
        # if enough transactions mine
        if len(self.new_block.transactions) == self.capacity:
            self.blockchain.mine_block(block)
        # append transaction to block
        else:
            self.new_block.transactions.append(transaction)
        # return True


    def valid_block(self, block):
        #Transform the json to block object
        self.mining = False
        block_index = block["index"]
        block_timestamp = block["timestamp"]
        block_transactions = block["transactions"]
        block_nonce = block["nonce"]
        block_previous_hash = block["previous_hash"]
        block_to_test = Block(block_index, block_transactions, block_nonce, block_previous_hash, block_timestamp)
        transactions_ids_in_block = []
        # which transactions are in the block?
        for i in range(len(block_to_test.transactions)):
            transactions_ids_in_block.append(block_to_test.transactions[i]["transaction_id"])
        # which transactions I should get rid of?
        get_rid = [i for i in self.pending_transactions if (i["transaction_id"] in transactions_ids_in_block)]
        #verify the new block we got
        if self.blockchain.validate_block(block_to_test, self.difficulty) and len(get_rid)!=0:#I will actually benefit from testing this block
            block_to_test.current_hash = block_to_test.get_hash_obj().hexdigest()
            #remove these transactions from our pending block
            self.pending_transactions = [i for i in self.pending_transactions if not(i["transaction_id"] in transactions_ids_in_block)]
            #add the confirmed block tou our chain
            self.blockchain.add_block(block_to_test)
        #maybe we have the wrong blockchain?
        elif len(get_rid) != 0:  # if we dont get rid of items then we don't care
            if self.blockchain.resolve_conflict():
                block_to_test = self.blockchain.blocks[-1]
                # remove these transactions from our pending block
                self.pending_transactions = [i for i in self.pending_transactions if
                                             not (i["transaction_id"] in transactions_ids_in_block)]
        print(self.blockchain)
        #keep the dream alive
        if len(self.pending_transactions)!=0:
            self.mine_new_block()
        return
