import time
from collections import OrderedDict
from hashlib import sha256


class Block:
	def __init__(self, index, transactions, nonce, previous_hash=0):

		self.index = index						# Block Identification
		self.timestamp = time.time()			# Time created
		self.transactions = transactions		# Block's Transactions
		self.nonce = nonce						# Proof of work
		self.current_hash = None				# Current hash
		self.previous_hash = previous_hash		# Connecting hash to previous block

		self.od = None

	def to_od(self):

		od = OrderedDict([
			('index', self.index),
			('timestamp', self.timestamp),
			('transactions', ([trans.to_od() for trans in self.transactions])),
			('nonce', self.nonce),
			('current_hash', self.current_hash),
		])

		# store it for future usage
		self.od = od

		return self.od

	def get_hash(self):

		# If not ordered dict, create one
		if self.od is None:
			self.od = self.to_od()

		# Calculate hash only if not available, avoid calculations
		if self.current_hash is None:
			self.current_hash = sha256(str(self.od).encode()).hexdigest()

		return self.current_hash
