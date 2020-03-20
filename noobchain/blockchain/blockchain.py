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

	def __str__(self):
		chain = f'{self.genesis.index} ({0})'

		# ignore genesis
		for block in self.blocks[1:]:
			chain += f'{block.index} ({block.current_hash.hexdigest()}) -> '

		return chain[:-4]

	def add_block(self, new_block):
		self.blocks.append(new_block)

		return self

	def proof_of_work(self, difficulty):

		# grab hash of latest block in the chain
		prev_hash = self.blocks[-1].get_hash()
		proof = 0
		prev_hash.update(f'{proof}{prev_hash.hexdigest()}'.encode('utf-8'))

		while prev_hash.hexdigest()[:difficulty] != '0'*difficulty:
			prev_hash.update(f'{proof}{prev_hash.hexdigest()}'.encode('utf-8'))
			proof += 1

		return proof


