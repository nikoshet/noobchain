from noobchain.Wallet import Wallet
from Crypto.PublicKey import RSA
import re
import requests
from flask import jsonify
from noobchain.Block import Block
from noobchain.Blockchain import Blockchain
from noobchain.main import capacity, difficulty

class Node:

    def __init__(self, ip, port, is_bootstrap, ip_of_bootstrap, port_of_bootstrap, no_of_nodes):

        self.ip = ip
        self.port = port
        self.no_of_nodes = no_of_nodes
        self.value = 0
        self.address = self.get_address(self.ip, self.port)
        # Here we store information for every node, as its id, its address (ip:port) its public key and its balance
        bootstrap_address = self.get_address(ip_of_bootstrap, port_of_bootstrap)
        self.ring = [{id: str.join('id', str(0)), 'address': bootstrap_address}]

        # Get a public key and a private key with RSA
        self.public, self.private = self.first_time_keys()
        # Create wallet
        self.wallet = self.generate_wallet(self.public, self.private)

        self.bkchain = Blockchain()
        self.new_block = 0
        self.trans = 0
        # Check if node is bootstrap
        self.is_bootstrap = is_bootstrap

        if self.is_bootstrap:
            self.create_genesis_block()
            #self.start(ip_of_bootstrap, port_of_bootstrap, ip_of_bootstrap, port_of_bootstrap)
        #else:
        #    self.start(ip, port, ip_of_bootstrap, port_of_bootstrap, )

        # Search database for user (use conn)
        #db = []
        #if id in db:
        #    self.public = self.get_public(id=id)
        #    self.private = self.get_private(id=id)
        #else:
        #    self.id = id

    def __str__(self):
        return f'------ PRINTING DETAILS FOR USER: [{self.id}] ------' \
               f'\n{self.name} {self.surname}' \
               f'\nPublic key:\n{self.public}' \
               f'\nPrivate key:\n{self.private}'

    ### General functions ###

    # Return address of ip, port
    def get_address(self, ip, port):
        return 'http://' + str(ip) + ':' + str(port)

    # Get a public key and a private key with RSA
    def first_time_keys(self):
        # https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html#Crypto.PublicKey.RSA.generate
        # Generate random RSA object
        private_key = RSA.generate(2048)
        public_key = private_key.publickey()

        # exportKey, format param: "PEM" -> string
        #                          "DER" -> binary

        # Remove conventions
        # '-----BEGIN PUBLIC KEY-----\n', '\n-----END PUBLIC KEY-----'
        public_key = public_key.exportKey().decode('utf-8')
        public_key = re.sub('(-----BEGIN PUBLIC KEY-----\\n)|(\\n-----END PUBLIC KEY-----)', '', public_key)

        # '-----BEGIN RSA PRIVATE KEY-----\n, '\n-----END RSA PRIVATE KEY-----'
        private_key = private_key.exportKey().decode('utf-8')
        private_key = re.sub('(-----BEGIN RSA PRIVATE KEY-----\\n)|(\\n-----END RSA PRIVATE KEY-----)', '', private_key)

        return public_key, private_key

    # Create a wallet for this node
    def generate_wallet(self, publ, priv):
        wall = Wallet(publ, priv)
        return wall

    # Create first block of blockchain (for Bootstrap)
    def create_genesis_block(self):
        self.create_new_block(previous_hash=1, nonce=0)
        self.trans = self.create_transaction(0, self.wallet.public_key, 0, self.no_of_nodes * 100)
        self.add_transaction_to_block(self, self.new_block, self.trans)

    def register_node_to_ring(self, node_ip, node_port):
        # Add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
        # Bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
        # message.ip = node_ip
        # message.port = node_port
        # Answer to node
        self.respond_to_node(node_ip, node_port)

        # Broadcast ring to all nodes
        if len(self.ring == self.no_of_nodes):
            self.broadcast_ring_to_nodes()

    def respond_to_node(self, node_ip, node_port):
        value = 100
        message = {'sender': 'http://' + self.ip + ':' + self.port, 'receiver': 'http://' + node_ip + ':' + node_port,
                   'value': value}
        req = requests.post('http://' + node_ip + ':' + node_port, jsonify(message))
        #if len(self.ring) == self.no_of_nodes:
        #    self.broadcast_ring_to_nodes()

    def broadcast_ring_to_nodes(self):
        for member in self.ring:
            address = member.get('address')
            requests.post(address + "/broadcast/block", data=jsonify(self.ring))

    ### Transaction functions ###

    def create_transaction(self, sender, receiver, signature, value):
        trans_input = 0  # previous_output_id
        trans_output = {'id_of_transaction': 1, 'receiver': receiver,
                        'sender': sender, 'value': value, 'signature': signature}
        my_trans = 0
        # remember to broadcast it
        self.broadcast_transaction(my_trans)
        return my_trans

    def broadcast_transaction(self, transaction):
        print('Broadcasting transaction')
        message = {}
        # Post message in ring except me
        for member in self.ring:
            address = member.get('address')
            if address != self.address:
                # Post request
                # send to ring.sender
                requests.post(address+"/transactions/create", data=message)

    def validate_transaction(self, transaction, signature, sender):
        # Use of signature and NBCs balance
        # if verify_signature and
        # if utxo ok
        return True  # else False

    def verify_signature(self):
        return True

    ### Block functions ###

    def create_new_block(self, previous_hash, nonce):
        new_block_index = len(self.bkchain.blocks)
        self.new_block = Block(new_block_index, nonce, previous_hash)
        return True

    def add_transaction_to_block(self, block, transaction):
        # if transaction is for genesis block
        if len(self.bkchain.blocks) == 0:
            self.mine_block(block)
        # if enough transactions mine
        if len(self.new_block.transactions) == capacity:
            self.mine_block(block)
        # append transaction to block
        else:
            self.new_block.transactions.append(transaction)
        #return True

    def mine_block(self, blk):
        return True

    def broadcast_block(self, new_block):
        message = new_block #{}
        for member in self.ring:
            address = member.get('address')
            if address != self.address:
                # request POST block to member
                requests.post(address + "/broadcast/block", data=message)
                #return True

    def valid_proof(self):
        MINING_DIFFICULTY = difficulty
        return True

    ### Concencus functions ###

    # def validate_chain(self):

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
