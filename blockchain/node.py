import Crypto as Crypto
#import RSA as RSA
from Crypto.PublicKey import RSA
import time
import wallet
import block
from flask import Flask, jsonify, request
import requests

class Node:

	def __init__(self, ip, port, is_bootstrap, ip_of_bootstrap, port_of_bootstrap, no_of_nodes):

		self.ip = ip
		self.port = port
		self.current_id_count = 0
		self.no_of_nodes = no_of_nodes
		self.NBC = 0
		self.wallet = {}
		# Here we store information for every node, as its id, its address (ip:port) its public key and its balance
		self.ring = [{'ip': ip_of_bootstrap, 'port': port_of_bootstrap}]
		self.is_bootstrap = is_bootstrap

		if self.is_bootstrap:
			self.start(ip_of_bootstrap, port_of_bootstrap, ip_of_bootstrap, port_of_bootstrap)
			self.create_genesis_block()
		else:
			self.start(ip, port, ip_of_bootstrap, port_of_bootstrap,)


	def start(self, ip, port, ip_of_bootstrap, port_of_bootstrap):

		# Create wallet
		self.wallet = self.generate_wallet()

		# Get size of ring and find id count
		#self.current_id_count = 1

	def create_genesis_block(self):
		self.create_new_block(previous_hash=1,nonce=0)

	def create_new_block(self,previous_hash,nonce):
		return True

	def generate_wallet(self):
		# Create a wallet for this node, with a public key and a private key
		# with RSA
		random_generator = Crypto.Random.new().read
		private_key = RSA.generate(1024, random_generator)

		public_key = private_key.publickey()
		wall = wallet.Wallet(public_key, private_key)
		return wall



	def register_node_to_ring(self, node_ip, node_port):
		# Add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		# Bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
		#message.ip = node_ip
		#message.port = node_port
		# Answer to node
		self.respond_to_node(node_ip, node_port)

		# Broadcast ring to all nodes
		if len(self.ring == self.no_of_nodes):
			self.broadcast_ring_to_nodes()

	def respond_to_node(self, node_ip, node_port):
		value = 100
		message = {'sender': 'http://'+self.ip+':'+self.port, 'receiver': 'http://'+node_ip+':'+node_port, 'value': value}
		req = requests.post('http://' + node_ip + ':' + node_port, jsonify(message))
		if len(self.ring) == self.no_of_nodes:
			self.broadcast_ring_to_nodes()

	def broadcast_ring_to_nodes(self):
		for n in self.ring:
			node_ip = n.get('ip')
			node_port = n.get('port')
			req = requests.post('http://'+node_ip+':'+node_port, jsonify(self.ring))

	def create_transaction(self, sender, receiver, signature):
		trans_input = 0 # previous_output_id
		trans_output = {'id_of_transaction':1,'receiver':0, 'sender':0,'money':1}
		my_trans = 0
		# remember to broadcast it
		self.broadcast_transaction(my_trans)

	def broadcast_transaction(self, transaction):
		print('Broadcasting transaction')
		sender_message = {}
		# Post message in ring except me
		for member in self.ring:
			if member.ip != self.ip:
				# Post request
				# send to ring.sender
				return True

	def validate_transaction(self, transaction, signature, sender):
		# Use of signature and NBCs balance
		# if verify_signature and
		# if utxo ok
		return True # else False

	def verify_signature(self):
		return True

	def add_transaction_to_block(self):
		#if enough transactions  mine
		return True

	def mine_block(self):
		return True

	def broadcast_block(self):
		for member in self.ring:
			if member.ip != self.ip:
				#request POST block to member
				return True

	def valid_proof(self):# , .., difficulty=MINING_DIFFICULTY):
		return True


	# Concencus functions

	#def validate_chain(self):

	def validate_block(self, chain):
		# Check for the longer chain across all nodes
		for np_of_block in range(1, len(chain)):
			block = chain[np_of_block]
			if not self.valid_proof(block) or block['previous_hash'] != chain[np_of_block-1].hash:
				return False # resolve_conflict(block)

	def resolve_conflict(self, block):
		# Resolve correct chain
		# Get blockchain size from all nodes and keep largest
		return True
