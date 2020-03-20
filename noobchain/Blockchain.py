import Block


class Blockchain:
	def __init__(self):

		self.blocks = []

	def add_block(self, new_block):
		self.blocks.append(new_block)
		# add a block to the blockchain
