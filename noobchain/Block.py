
import Blockchain


class Block:
	def __init__(self, index, timestamp, transactions, nonce, current_hash, previous_hash):

		self.index
		self.timestamp
		self.transactions
		self.nonce
		self.current_hash
		self.previous_hash

	def my_hash(self):
		#calculate self.hash
		return self.current_hash

	def add_transaction(self,transaction, blockchain):
		#add a transaction to the block
		return True