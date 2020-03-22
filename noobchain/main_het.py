# Import libraries
import psutil
from flask import Flask, render_template, request, jsonify, session
from argparse import ArgumentParser
from threading import Thread
import time
import json
from hashlib import sha256
from backend.node import Node
from backend.transaction import Transaction
from backend.block import Block
from backend.blockchain import Blockchain
#from views import layout_views, blockchain_views

app = Flask(__name__, static_folder='static')
app.secret_key = 'sec_key'
app.config['DEBUG'] = False

# Arguments
parser = ArgumentParser()
parser.add_argument('-ip', default='0.0.0.0', type=str, help='ip of node')
parser.add_argument('-p', '--port', default=1000, type=int, help='port to listen on')
parser.add_argument('-bootstrap', default='True', type=str, help='is node bootstrap?')
parser.add_argument('-ip_bootstrap', default='0.0.0.0', type=str, help='ip of bootstrap')
parser.add_argument('-port_bootstrap', default=1000, type=int, help='port of bootstrap')
parser.add_argument('-nodes', default=2, type=int, help='number of nodes')
parser.add_argument('-cap', default=2, type=int, help='capacity of blocks')
parser.add_argument('-dif', default=4, type=int, help='difficulty')
#args = parser.parse_args()
args, _ = parser.parse_known_args()
HOST = args.ip
PORT = args.port
if args.bootstrap == 'True':
    boot = True
else:
    boot = False
ip_of_bootstrap = args.ip_bootstrap
port_of_bootstrap = args.port_bootstrap
no_of_nodes = args.nodes
capacity = args.cap
difficulty = args.dif


# Register Views
#app.register_blueprint(layout_views.blueprint)            # Page Navigation
#app.register_blueprint(blockchain_views.blueprint)        # Functionality



new_node = Node(HOST, PORT, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes)
##############################################################################################
# View last transactions in the backend
@app.route('/transactions/view', methods=['GET'])
def get_transactions():
    # transactions = Blockchain.transactions
    response = 0  # {'transactions': transactions}
    return render_template("view_last_transactions.html")


# Show balance
@app.route('/show_balance', methods=['GET'])
def show_balance():
    # transactions = backend.transactions
    response = 0  # {'transactions': transactions}
    return render_template("show_balance.html")


# Create a transaction
@app.route('/transactions/create', methods=['POST'])
def create_transaction():
    message = json.loads(request.get_json())
    transaction = json.loads(message.get('transaction'))
    signature = transaction.get('signature')
    sender = transaction.get('sender_address')
    new_node.validate_transaction(transaction, signature, sender)
    response = 'success'
    return jsonify(response), 200


# Broadcast node ring to other nodes
@app.route('/broadcast/ring', methods=['POST'])
def broadcast_ring():
    message = request.get_json()
    #print(message)
    new_node.ring = json.loads(message)
    response = 'success'
    return jsonify(response), 200


# Broadcast block to other nodes
#@app.route('/broadcast/block/<int:node_id>', methods=['POST'])
#def broadcast_block(node_id):
@app.route('/broadcast/block/', methods=['POST'])
def broadcast_block():
    '''
    Post to http://127.0.0.1:5000/broadcast/block/ as json, the following
    {
    "index": 1,
    "timestamp": 1584806317.2038882,
    "transactions": [
        {
            "sender_address": "sender_public_key",
            "receiver_address": "receiver_public_key",
            "amount": 5,
            "transaction_id": 0,
            "transaction_inputs": 0,
            "transaction_outputs": "{1, (4, 1)}",
            "signature": ""
        },
        {
            "sender_address": "sender_public_key",
            "receiver_address": "receiver_public_key",
            "amount": 5,
            "transaction_id": 1,
            "transaction_inputs": 0,
            "transaction_outputs": "{1, (4, 1)}",
            "signature": ""
        }
    ],
    "nonce": 0,
    "current_hash": null
    }
    '''

    # get json post
    data = request.get_json()

    # Convert back to ordered dictionary
    #data = json.loads(data, object_pairs_hook=OrderedDict)

    print(f'Received: {data}')
    response = 0
    return jsonify(response), 200

# Register node to bootstrap ring
@app.route('/nodes/register', methods=['POST'])
def register_node():
    message = request.get_json()
    print(message)
    new_node.register_node_to_ring(message)
    response = 'success'
    return jsonify(response), 200

#------------------------------------
# Home page
@app.route('/')
def home():
    # Store host ip and port
    #session['HOST'] = HOST
    #session['PORT'] = PORT
    # Keep track of current page
    session['viewing'] = 'home'
    # pass data to page call
    data = {
        'CPU_PERCENT': psutil.cpu_percent(),
        'MEM_PERCENT': psutil.virtual_memory()[2]
    }
    return render_template('home.html', data=data)


# Help
@app.route('/help', methods=['GET'])
def help():
    session['viewing'] = 'help'
    return render_template('help.html')


# About
@app.route('/about', methods=['GET'])
def about():
    session['viewing'] = 'about'
    return render_template("about.html")


# Contact
@app.route('/contact', methods=['GET'])
def contact():
    session['viewing'] = 'contact'
    return render_template("contact.html")


# Frequently Asked Questions
@app.route('/faq', methods=['GET'])
def faq():
    session['viewing'] = 'faq'
    return render_template("faq.html")


# User's Profile
@app.route('/profile', methods=['GET'])
def profile():
    session['viewing'] = 'profile'
    return render_template("profile.html")

##############################################################################################



#print('\n------------------------------------------------------------------')
#print('Testing\n\n')
## Dummy variables
#sender_address = 'sender_public_key'
#receiver_address = 'receiver_public_key'
#amount = 5
#transaction_inputs = 0
#transaction_outputs = {1, (4, 1)}
## create new transaction
#t1 = Transaction(sender_address=sender_address, receiver_address=receiver_address, amount=amount,
#                 transaction_inputs=transaction_inputs, transaction_outputs=transaction_outputs)
#t1.hash()
#t2 = Transaction(sender_address=sender_address, receiver_address=receiver_address, amount=amount,
#                 transaction_inputs=transaction_inputs, transaction_outputs=transaction_outputs)
#t2.hash()
#print(f'Transactions Example\n{t1.od}')
#print(f'Hash: {t1.current_hash}')
#blockchain = Blockchain()
#block = Block(index=1, transactions=[t1, t2], nonce=0, previous_hash=0)
## Hash block
#block.hash()
#print(f'\nBlock Details example\n{block.od}')
#print(f'Hash: {block.current_hash}')
#print(f'\nJson dump:\n{json.dumps(block.od, default=str)}')
#blockchain.add_block(block)
#print('\nBlockchain example')
#print(blockchain)
#print(f'\nProof of Work for {blockchain.blocks[-1].current_hash}: {blockchain.mine_block(difficulty=2)}\n')
#print('------------------------------------------------------------------\n')


# .......................................................................................
# Function for node
#def start_new_node(ip, port, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes):
#    time.sleep(3)
#    print("New node")
#    new_node = Node(ip, port, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes)


print(f'Inputs: {HOST}, {PORT}, {boot}, {ip_of_bootstrap}, {port_of_bootstrap}, {no_of_nodes}, {capacity}, {difficulty}')
# Start node
#t_node = Thread(target=start_new_node, args=(HOST, PORT, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes))
#t_node.start()

#def start_new_flask_app(ip, port):
#    app.run(host=ip, port=port, debug=False, use_reloader=False)
    #from waitress import serve
    #serve(app, host=ip, port=port)

if __name__ == '__main__':
    #global new_node
    #new_node = Node(HOST, PORT, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes)
    #time.sleep(1)
    # Start Flask app
    from waitress import serve
    serve(app, host=HOST, port=PORT) #, debug=True, use_reloader=False)
    #app.run(host=HOST, port=PORT, debug=False, use_reloader=False) #True
    #time.sleep(3)

    #t_app = Thread(target=start_new_flask_app, args=(HOST, PORT))
    #t_app.start()