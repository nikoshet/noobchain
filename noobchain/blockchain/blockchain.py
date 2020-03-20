from noobchain.blockchain.block import Block


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
		# add a block to the blockchain
