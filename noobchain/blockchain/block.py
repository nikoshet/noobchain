import time


class Block:
	def __init__(self, index, transactions, nonce, current_hash=0, previous_hash=0):

		self.index = index						# Block Identification
		self.timestamp = time.time()			# Time created
		self.transactions = transactions		# Block's Transactions
		self.nonce = nonce						# Proof of work
		self.current_hash = current_hash		# Current hash
		self.previous_hash = previous_hash		# Connecting hash to previous block
