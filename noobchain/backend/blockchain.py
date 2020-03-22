from backend.block import Block
from backend.transaction import Transaction
import json
import requests


class Blockchain:
    def __init__(self, ring):

        self.ring = ring  # List of ring nodes

        # Genesis block
        self.genesis = Block(index=0, previous_hash=1, transactions=[], nonce=0)

        # Genesis transaction
        transaction = Transaction(sender_address=0, receiver_address=self.ring[0]['public_key'], amount=500,
                                  transaction_inputs='', transaction_outputs='', genesis=True)

        self.genesis.transactions.append(transaction)
        self.genesis.hash(genesis=True)

        self.blocks = []  # List of added blocks
        self.add_block(self.genesis)

        self.public_key = 'a_public_key'

        self.resolve_conflict = False  # Check chain updates (bigger was found)

    def __str__(self):
        chain = f'{self.genesis.index} ({0}) '

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

        # TODO
        # Fix code below for open transactions (if capacity > 1?!?!)
        #copied_transactions = self.__open_transactions[:]
        #for tx in copied_transactions:
        #    if not Wallet.verify_transaction(tx):
        #        return None

        #copied_transactions.append(reward_transaction)
        block = Block(index=len(self.blocks), previous_hash=self.blocks[-1].current_hash,
                      transactions=[], nonce=nonce)
        block.hash()

        print(f'\nBlock to broadcast: {block.to_json()}')
        self.blocks.append(block)
        # Actually post it at http://{address}/broadcast/block
        # self.broadcast_block(block)
        return self

    def broadcast_block(self, block):
        for member in self.ring:
            url = f'{member.get("address")}/broadcast/block/'
            response = requests.post(url, block.to_json())
            if response.status_code == 400 or response.status_code == 500:
                print('Block declined, needs resolving')

            if response.status_code == 409:
                self.resolve_conflicts = True

        return self

    def resolve(self):

        for member in self.ring:
            # Request chain from nodes
            new_blocks = requests.get(f'http://{member.get("address")}/chain').json()

            # Build it using json
            new_blocks = [Block(block['index'], block['timestamp'], block['nonce'],
                                [Transaction(t['sender_address'], t['receiver_address'], t['amount'], t['transaction_id'],
                                             t['transaction_inputs'], t['transaction_outputs'], t['signature'])
                                 for t in block['transactions']])
                          for block in new_blocks]

            print(f'\nCollected chain {new_blocks}\n')
            # If bigger is to be found, replace existing chain
            if len(new_blocks) > len(self.blocks) and self.verify_blocks(new_blocks):
                self.blocks = new_blocks

        self.resolve_conflict = False

        return self


# ---------------------------------------------- VERIFICATION FUNCTIONS ----------------------------------------------

    def verify_blocks(self, blockchain):

        # Loop chain to validate that hashes are connected
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != blockchain[index - 1].current_hash:
                return False

        return True
