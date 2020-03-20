from noobchain.blockchain.block import Block
from hashlib import sha256


class Blockchain:
	def __init__(self):

		# First block ever
		# TODO
		# transactions in genesis block should contain only 1 transaction
		# 100*n -> Bootstrap from Wallet (ip=0).
		self.genesis = Block(index=0, previous_hash=1, transactions=[], nonce=0)

		# List of added blocks
		self.blocks = [self.genesis]

	def add_block(self, new_block):
		self.blocks.append(new_block)

		return self

	def proof_of_work(self, difficulty):

		# grab last block of chain
		block_last = self.blocks[-1]
		last_hash = block_last.previous_hash
		proof = 0

		# Join all transactions in block
		transactions = str([transaction.to_json().digest() for transaction in block_last.transactions])

		while not sha256(transactions + str(last_hash) + str(proof))[:difficulty] == '0'*difficulty:
			proof += 1

		return proof


