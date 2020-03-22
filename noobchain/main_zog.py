# Import libraries
from flask import Flask, jsonify
from argparse import ArgumentParser
from threading import Thread
import time
import json
from hashlib import sha256
from noobchain.backend.node import Node
from noobchain.backend.transaction import Transaction
from noobchain.backend.block import Block
from noobchain.backend.blockchain import Blockchain
from noobchain.views import layout_views, blockchain_views


app = Flask(__name__, static_folder='static')
app.config['DEBUG'] = True

# Register Views
app.register_blueprint(layout_views.blueprint)            # Page Navigation
app.register_blueprint(blockchain_views.blueprint)        # Functionality

#HOST = '127.0.0.1'
#PORT = 4000

# Arguments
parser = ArgumentParser()
parser.add_argument('-ip', default='127.0.0.1', type=str, help='ip of node')
parser.add_argument('-p', '--port', default=1000, type=int, help='port to listen on')
parser.add_argument('-bootstrap', default=True, type=bool, help='is node bootstrap?')
parser.add_argument('-ip_bootstrap', default='127.0.0.1', type=str, help='ip of bootstrap')
parser.add_argument('-port_bootstrap', default=1000, type=int, help='port of bootstrap')
parser.add_argument('-nodes', default=5, type=int, help='number of nodes')
parser.add_argument('-cap', default=1, type=int, help='capacity of blocks')
parser.add_argument('-dif', default=4, type=int, help='difficulty')
#args = parser.parse_args()
args, _ = parser.parse_known_args()
HOST = args.ip
PORT = args.port
boot = args.bootstrap
ip_of_bootstrap = args.ip_bootstrap
port_of_bootstrap = args.port_bootstrap
no_of_nodes = args.nodes
capacity = args.cap
difficulty = args.dif


print('\n-------------------------------------------------------------------------------------------------------------')
print(f'Inputs: {HOST}, {PORT}, {boot}, {ip_of_bootstrap}, {port_of_bootstrap}, {capacity}, {difficulty}')
print('\n-------------------------------------------------------------------------------------------------------------')
print('Testing\n')


# Get current node's version of chain
@app.route('/receive/chain', methods=['GET'])
def get_chain():
    blockchain_json = [block.to_json() for block in blockchain.blocks]

    return jsonify(blockchain_json), 200


# Create bootstrap node
bootstrap = Node(ip=HOST, port=PORT, is_bootstrap=True, ip_of_bootstrap=ip_of_bootstrap,
                 port_of_bootstrap=port_of_bootstrap, no_of_nodes=no_of_nodes)

print(f'Bootstrap public key: {bootstrap.public},\n\nPrivate key: {bootstrap.private}\n')
print(f'Ring {bootstrap.ring}')

# Dummy variables
sender_address = 'sender_public_key'
receiver_address = 'receiver_public_key'
amount = 5
transaction_inputs = 0
transaction_outputs = {1, (4, 1)}

# create new transaction
t1 = Transaction(sender_address=sender_address, receiver_address=receiver_address, amount=amount,
                 transaction_inputs=transaction_inputs, transaction_outputs=transaction_outputs)
t1.signature = 'dummy1'


t2 = Transaction(sender_address=sender_address, receiver_address=receiver_address, amount=amount,
                 transaction_inputs=transaction_inputs, transaction_outputs=transaction_outputs)
t2.signature = 'dummy2'

print(f'Transactions Example\n{t1.to_json()}')

blockchain = Blockchain(bootstrap.ring)
block = Block(index=1, transactions=[t1, t2], nonce=0, previous_hash=0)

# Hash block
block.hash()

print(f'\nBlock Details example\n{block.to_json()}')
print(f'Hash: {block.current_hash}')

blockchain.add_block(block)

print(f'\nBlockchain example\n{blockchain}\n')
blockchain.mine_block(difficulty=2)

print('-------------------------------------------------------------------------------------------------------------\n')


# .......................................................................................
# Function for node
def start_new_node(ip, port, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes):
    print("New node")
    new_node = Node(ip, port, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes)





# Save HOST, PORT as cookies
# res = make_response('Setting up Cookies')
# res.set_cookie('host', HOST)
# res.set_cookie('port', PORT)


if __name__ == '__main__':

    # Start Flask app
    app.run(host=HOST, port=PORT, debug=True)