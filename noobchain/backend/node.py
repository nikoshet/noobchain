import time
from threading import Thread
import json
from backend.wallet import Wallet
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import os
import requests
from flask import jsonify
from backend.block import Block
from backend.blockchain import Blockchain
from backend.transaction import Transaction
from collections import OrderedDict
from base64 import b64decode
from copy import deepcopy


class Node:

    def __init__(self, ip, port, is_bootstrap, ip_of_bootstrap, port_of_bootstrap, no_of_nodes, capacity, difficulty):

        self.ip = ip
        self.port = port
        self.no_of_nodes = no_of_nodes
        self.id = ''
        self.address = self.get_address(self.ip, self.port)
        self.pending_transactions = []

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
        self.mining = True

        self.capacity = capacity
        self.difficulty = difficulty

        # Check if node is bootstrap
        self.is_bootstrap = is_bootstrap

        if self.is_bootstrap:
            self.id = 'id0'
            self.wallet.utxos["id00"]=self.no_of_nodes*100
            self.blockchain = Blockchain(self.ring,self.id, self.no_of_nodes)

        else:
            self.wallet.others_utxos["id0"] = [("id00", self.no_of_nodes*100)]

            # Not sure about the runtime of this thread, uncomment
            Thread(target=self.register_on_bootstrap).start()
            #self.register_on_bootstrap()

        # Thread that permanently reads transactions until they are done
        Thread(target=self.read_file).start()

        # Thread that permanently attempts to mine if there are enough transactions
        Thread(target=self.mine).start()

    def mine(self):

        while True:
            if len(self.pending_transactions) <= self.capacity:
                time.sleep(5)

            else:
                # Update pending Transactions
                self.remove_trans()

                # Create objects for first n (n = capacity)
                transactions = []

                # Load transactions for that block
                for t in self.pending_transactions[:self.capacity]:
                    transaction = Transaction(sender_address=t["sender_address"],
                                              receiver_address=t["receiver_address"],
                                              amount=int(t["amount"]), wallet=None,
                                              transaction_inputs=t["transaction_inputs"],
                                              ids=t["node_id"])

                    transaction.transaction_id = t["transaction_id"]
                    transaction.signature = t["signature"]
                    transaction.transaction_outputs = t["transaction_outputs"]
                    transaction.change = int(t["change"])

                    transactions.append(transaction)

                # Create block instance for those transactions
                block = Block(index=len(self.blockchain.blocks) + 1, nonce=0,
                              transactions=transactions,
                              previous_hash=self.blockchain.blocks[-1].current_hash)

                # Mine block
                block = self.blockchain.mine_block(block=block, difficulty=self.difficulty)

                # When finish, broadcast it
                self.blockchain.broadcast_block(block)


    def __str__(self):
        return f'------ PRINTING DETAILS FOR USER: [{self.ip}] ------' \
               f'\n{self.ip} {self.port}' \
 \
    ### General functions ###

    def register_on_bootstrap(self):
        time.sleep(2)
        message = {'public_key': self.wallet.public_key, 'address': self.address}
        print('Resource:', self.ring[0]['address'] + "/nodes/register")
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

    def register_node_to_ring(self, message):
        # Add the new node to ring
        # Bootstrap node informs all other nodes and gives the new node an id and 100 NBCs
        node_address = message.get('address')
        public_key = message.get('public_key')
        self.ring.append({'id': str.join('id', str(len(self.ring))), 'public_key': public_key, 'address': node_address})
        #print(self.ring)

        # Broadcast ring to all nodes
        if len(self.ring) == self.no_of_nodes:
            #Thread(target=self.broadcast_ring_to_nodes).start()
            #Thread(target=self.respond_to_node).start()
            self.broadcast_ring_to_nodes()
            self.respond_to_node()

    def respond_to_node(self):
        value = 100
        i = 1
        for member in self.ring:
            address = member.get('address')
            if address != self.address:
                print('Responding to node:', i)
                i += 1
                # address = member.get('address')
                public_key = member.get('public_key')
                # message = {'sender': self.address, 'receiver': address,
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
                    print('Error:', req.status_code)
                else:
                    print('Successful registration on bootstrap node from node:', address)


    ### Transaction functions ###

    def create_transaction(self, sender_address, receiver_address, value):
        tmp = 0
        trans_input = []
        for key, available in self.wallet.utxos.items():
            if tmp < value:
                trans_input.append(key)
                tmp += available
        my_trans = Transaction(sender_address=sender_address, receiver_address=receiver_address, amount=value,
                               transaction_inputs=trans_input, wallet=self.wallet, ids=self.id)
        my_trans.signature = Wallet.sign_transaction(self.wallet, my_trans)

        message = {'transaction': my_trans.to_json()}
        self.broadcast_transaction(message)

    def broadcast_transaction(self, message):
        print('Broadcasting transaction')
        # Post message in ring except me
        for member in self.ring:
            address = member.get('address')
            if address != self.address:
                # Post request
                # send to ring.sender
                req = requests.post(address + "/broadcast/transaction", json=json.dumps(message))
                if not req.status_code == 200:
                    print('Error:', req.status_code)

        # also broadcast it to ourselves because we have the object and we want the json,
        # we are leveling everything between the boot and the nodes

        for member in self.ring:
            address = member.get('address')
            if address == self.address:
                # Post request
                # send to ring.sender
                req = requests.post(address + "/broadcast/transaction", json=json.dumps(message))
                if not req.status_code == 200:
                    print('Error:', req.status_code)

    def validate_transaction(self, t, signature, sender):

        transaction = Transaction(sender_address=t["sender_address"],
                                  receiver_address=t["receiver_address"],
                                  amount=int(t["amount"]), wallet=None,
                                  transaction_inputs=t["transaction_inputs"],
                                  ids=t["node_id"])

        transaction.transaction_id = t["transaction_id"]
        transaction.signature = t["signature"]
        transaction.transaction_outputs = t["transaction_outputs"]
        transaction.change = int(t["change"])

        # if I am not the bootstrap I dont have a blockchain
        if self.blockchain is None:
            self.blockchain = Blockchain(self.ring, self.id, self.no_of_nodes)

        # check signature and value of the transaction
        if self.verify_value(transaction) and self.verify_signature(transaction, sender):
            # if everything is good change the UTXOS
            self.update_utxos(transaction, self.wallet)
            # add to list of transactions
            # self.pending_transactions.append(transaction)

            self.pending_transactions.append(transaction.to_od())

            return True
        else:
            print('Error on validating')
            return False


    def verify_value(self, trans):

        # check that the utxos of the sender are enough to create this transaction and he is not cheating
        id_sender = trans.node_id
        amount = trans.amount
        to_be_checked = trans.transaction_inputs
        available_money = 0
        if id_sender == self.id:
            unspent_transactions = [(k, v) for k, v in self.wallet.utxos.items()] 
        else:
            unspent_transactions = self.wallet.others_utxos[id_sender]
        for unspent in unspent_transactions:
            if unspent[0] in to_be_checked:
                available_money += unspent[1]
        if available_money >= amount:
            return True
        else:
            print("\nNot Enough UTXOS:", 'amount:', amount, ', available money:', available_money)
            return False

    def verify_signature(self, trans, pub_key):
        # verify the signature of the sender
        # transform the json/dictionary to ordered dictionary format so that we have the same hash
        to_test = deepcopy(trans)
        to_test.signature = ""
        to_test = to_test.to_json()
        h = SHA.new(to_test.encode('utf8'))
        public_key = RSA.importKey(pub_key)
        sign_to_test = PKCS1_v1_5.new(public_key)

        if sign_to_test.verify(h, b64decode(trans.signature)):
            return True

        print("Wrong signature")
        return False

    def update_utxos(self,trans, portofoli):
        # state variables to check wheter I was involved in the transaction
        i_got_money = False
        i_got_change = False

        # find the sender and the receiver id from the ring
        for node in self.ring:
                if node["public_key"] == trans.receiver_address:
                    id_receiver = "id"+str(node["id"])
                if node["public_key"] == trans.sender_address:
                    id_sender = "id"+str(node["id"])

        # check wheter I have created a key in the dictionary for the ones in the current transaction
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

        # If I was the one getting money upgrade my utxos
        if trans.receiver_address == self.public:
            portofoli.utxos[list(trans.transaction_outputs[0].keys())[0]] = trans.transaction_outputs[0][list(trans.transaction_outputs[0].keys())[0]][1]
            i_got_money = True

        # If I was the one sending money delete the utxos that I used from wallet
        # and if I am expecting change create a new utxo with the change
        if trans.sender_address == self.public:
            for utxos_spend in trans.transaction_inputs:
                del portofoli.utxos[utxos_spend]
            if trans.transaction_outputs[1][list(trans.transaction_outputs[1].keys())[0]][1] > 0:
                portofoli.utxos[list(trans.transaction_outputs[1].keys())[0]] = trans.transaction_outputs[1][list(trans.transaction_outputs[1].keys())[0]][1]
            i_got_change = True

        # Again if I was the one that got money I have to fix the utxos of the sender
        if i_got_money:
            items_to_remove = []
            for item in portofoli.others_utxos[id_sender]:
                if item[0] in trans.transaction_inputs:
                    items_to_remove.append(item)
            for item in items_to_remove:
                portofoli.others_utxos[id_sender].remove(item)
            if trans.transaction_outputs[1][list(trans.transaction_outputs[1].keys())[0]][1] > 0:
                portofoli.others_utxos[id_sender].append((list(trans.transaction_outputs[1].keys())[0],
                                                          trans.transaction_outputs[1][list(trans.transaction_outputs[1].keys())[0]][1]))
        
        # if I get change, i.e. I spend more utxos than the value I wanted to send, I have to upgrade my utxos
        elif i_got_change:
             for node in self.ring:
                if node["public_key"] == trans.receiver_address:
                    id_receiver = "id"+str(node["id"])
                    break
            
             portofoli.others_utxos[id_receiver].append((list(trans.transaction_outputs[0].keys())[0],
                                                         trans.transaction_outputs[0][list(trans.transaction_outputs[0].keys())[0]][1]))

        # the last case is that I did not participate in this transaction so I have to upgrade the utxos of the sender
        # and the receiver, mind that for the sender I must delete the inputs of the transaction
        # and create new utxo if he got change
        else:
            portofoli.others_utxos[id_receiver].append((list(trans.transaction_outputs[0].keys())[0],
                                                        trans.transaction_outputs[0][list(trans.transaction_outputs[0].keys())[0]][1]))
            items_to_remove = []
            for item in portofoli.others_utxos[id_sender]:
                if item[0] in trans.transaction_inputs:
                    items_to_remove.append(item)
            for item in items_to_remove:
                portofoli.others_utxos[id_sender].remove(item)
            
            if trans.transaction_outputs[1][list(trans.transaction_outputs[1].keys())[0]][1] > 0:
                portofoli.others_utxos[id_sender].append((list(trans.transaction_outputs[1].keys())[0],
                                                          trans.transaction_outputs[1][list(trans.transaction_outputs[1].keys())[0]][1]))
        return


    def remove_trans(self):

        # done = []
        # for block in self.blockchain.blocks:
        #     for trans in block.transactions:
        #         done.append(trans.to_od())

        # dd = [trans for trans in self.pending_transactions if trans not in done]

        # Transactions that have already been done
        done = [trans.to_od() for block in self.blockchain.blocks for trans in block.transactions]

        # Keep transactions that you have validated, but they are not in blockchain
        self.pending_transactions = [trans for trans in self.pending_transactions if trans not in done]


    def valid_block(self, block_received):
        transactions = []

        # Load transactions for that block
        for t in block_received["transactions"]:
            transaction = Transaction(sender_address=t["sender_address"],
                                      receiver_address=t["receiver_address"],
                                      amount=int(t["amount"]), wallet=None,
                                      transaction_inputs=t["transaction_inputs"],
                                      ids=t["node_id"])

            transaction.transaction_id = t["transaction_id"]
            transaction.signature = t["signature"]
            transaction.transaction_outputs = t["transaction_outputs"]
            transaction.change = int(t["change"])

            # Dont need this?!
            transactions.append(transaction)

        block = Block(index=block_received["index"], transactions=transactions, nonce=block_received["nonce"],
                      previous_hash=block_received["previous_hash"], timestamp=block_received["timestamp"])

        block.current_hash = block.get_hash()

        # print('Current length of blockchain:', len(self.blockchain.blocks), 'blocks')

        if self.blockchain.validate_block(block, self.difficulty):

            # This block is validated, add it to the chain
            self.blockchain.add_block(block)

            # Update self transactions
            self.remove_trans()

            print(f'Just Added a Block to my chain! Current Length {len(self.blockchain.blocks)}.')
            print(f'Pending Transactions to do: {len(self.pending_transactions)}')

            return True

        # Reaching here means i failed to validate that block, therefore try to resolve my chain
        print(f'Failed to Validate that Block, forcing Blockchain Update')
        self.blockchain.resolve_conflict()
        return False

    # Function to read file for transactions
    def read_file(self):
        while len(self.ring) < self.no_of_nodes:
            time.sleep(self.no_of_nodes * 5)

        my_path = os.path.abspath(os.path.dirname(__file__))
        file = os.path.join(my_path, f'../transactions/{self.no_of_nodes}nodes/transactions{self.id[2:]}.txt')
        print('Reading file of transactions!')
        with open(file, 'r') as file:
            for line in file:
                node_id, amount = line.split()

                # get address based on index
                receiver = self.ring[int(node_id[2:])].get('public_key')
                self.create_transaction(self.public, receiver, int(amount))
                # time.sleep(1)

        print('My transactions finished!')
