from backend.block import Block
from backend.transaction import Transaction
import json
import requests


class Blockchain:
    def __init__(self, ring):

        self.ring = ring  # List of ring nodes

        # Genesis block
        transaction = Transaction(sender_address=0, receiver_address=self.ring[0]['public_key'], amount=500,
                                  transaction_inputs='', transaction_outputs='', genesis=True)

        self.genesis = Block(index=0, previous_hash=1, transactions=[transaction], nonce=0)
        self.genesis.hash(genesis=True)

        self.blocks = [self.genesis]  # List of added blocks

        self.genesis.hash(genesis=True)

        self.blocks = [self.genesis]  # List of added blocks
        self.reward = 10  # Reward for mining
        self.public_key = 'a_public_key'


    def __str__(self):
        chain = f'{self.genesis.index} ({0})'

        # ignore genesis
        for block in self.blocks[1:]:
            chain += f'-> {block.index} ({block.current_hash})'

        return chain

    def add_block(self, new_block):
        self.blocks.append(new_block)

        return self

    def mine_block(self, difficulty):
        self.blocks[-1].hash()
        # grab hash of latest block in the chain
        prev_hash = self.blocks[-1].current_hash_obj
        nonce = 0

        # update hash
        prev_hash.update(f'{nonce}{prev_hash.hexdigest()}'.encode('utf-8'))

        # try new hashes until first n characters are 0.
        while prev_hash.hexdigest()[:difficulty] != '0' * difficulty:
            prev_hash.update(f'{nonce}{prev_hash.hexdigest()}'.encode('utf-8'))
            nonce += 1

        # create transaction for miner
        reward_transaction = Transaction(sender_address='MINING', receiver_address=self.public_key, amount=self.reward,
                                         transaction_inputs=1, transaction_outputs={0: (0, 0), 1: (0, 0)})
        reward_transaction.signature = 'MINING'

        # TODO
        # Fix code below for open transactions (if capacity > 1?!?!)
        #copied_transactions = self.__open_transactions[:]
        #for tx in copied_transactions:
        #    if not Wallet.verify_transaction(tx):
        #        return None

        #copied_transactions.append(reward_transaction)
        block = Block(index=len(self.blocks), previous_hash=self.blocks[-1].current_hash,
                      transactions=[reward_transaction], nonce=nonce)
        block.hash()

        print(f'\nBlock to broadcast: {block.to_od()}')
        self.blocks.append(block)
        # Actually post it at http://{address}/broadcast/block
        # self.broadcast_block(block)
        return self

    def broadcast_block(self, block):
        for member in self.ring:
            url = f'{member.get("address")}/broadcast/block/'
            response = requests.post(url, json=json.dumps(block.to_od(), default=str))
            if response.status_code == 400 or response.status_code == 500:
                print('Block declined, needs resolving')

            if response.status_code == 409:
                self.resolve_conflicts = True

        return self
