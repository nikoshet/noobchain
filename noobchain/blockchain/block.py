
import time
import uuid


class Block:
	def __init__(self, index, nonce, previous_hash):

		self.index = index
		self.timestamp = time.time()
		self.transactions = []
		self.nonce = uuid.uuid4().hex if nonce != 0 else 0
		self.previous_hash = previous_hash
		self.current_hash = 0

	def my_hash(self):
		#calculate self.hash
		return self.current_hash

	def add_transaction(self, transaction):
		#add a transaction to the block
		return True
