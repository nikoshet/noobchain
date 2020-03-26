# Import libraries
import psutil
from flask import Flask, render_template, request, jsonify, session
from argparse import ArgumentParser
from threading import Thread
import time
import json
from hashlib import sha256
from backend.node import Node
from backend.wallet import Wallet
from backend.transaction import Transaction
from backend.block import Block
from backend.blockchain import Blockchain
#from views import layout_views, blockchain_views
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
app.secret_key = 'sec_key'
app.config['DEBUG'] = False

# Arguments
parser = ArgumentParser()
parser.add_argument('-ip', default='0.0.0.0', type=str, help='ip of node')
#parser.add_argument('-ip', default='127.0.0.1', type=str, help='ip of node')
parser.add_argument('-p', '--port', default=1000, type=int, help='port to listen on')
parser.add_argument('-bootstrap', default='True', type=str, help='is node bootstrap?')
parser.add_argument('-ip_bootstrap', default='0.0.0.0', type=str, help='ip of bootstrap')
#parser.add_argument('-ip_bootstrap', default='127.0.0.1', type=str, help='ip of bootstrap')
parser.add_argument('-port_bootstrap', default=1000, type=int, help='port of bootstrap')
parser.add_argument('-nodes', default=5, type=int, help='number of nodes')
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



new_node = Node(HOST, PORT, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes, capacity, difficulty)

##############################################################################################
#----------------------------------------------------------------------#
#---------------------- REST API FOR BACKEND ---------------------------#
#----------------------------------------------------------------------#

# Respond with our chain to resolve conflicts
@app.route('/chain', methods=['GET'])
def send_chain():
    chain = new_node.blockchain.to_json()
    return jsonify(chain), 200

# View last transactions in the backend
@app.route('/transactions/view', methods=['GET'])
def get_transactions():
    # transactions = Blockchain.transactions
    response = 0  # {'transactions': transactions}
    return render_template("view_last_transactions.html")

# Create a transaction on frontend
@app.route('/transactions/create/browser', methods=['POST'])
def create_browser_transaction():
    sender = request.form['sender_address']
    receiver = request.form['receiver_address']
    amount = request.form['amount']
    trans = new_node.create_transaction(sender, receiver, int(amount))
    response = 'success'
    return jsonify(response), 200

# Create a transaction
@app.route('/transactions/create', methods=['POST'])
def create_transaction():
    trans = json.loads(request.get_json())
    sender = trans['sender_address']
    receiver = trans['receiver_address']
    amount = trans['amount']
    for node in new_node.ring:
        if node["id"]==sender[2:]: sender = node["public_key"]
        if node["id"]==receiver[2:]: receiver = node["public_key"]
    trans = new_node.create_transaction(sender, receiver, int(amount))
    response = 'success'
    return jsonify(response), 200

# Broadcast transaction
@app.route('/broadcast/transaction', methods=['POST'])
def broadcast_transaction():
    message = json.loads(request.get_json())
    transaction = json.loads(message.get('transaction'))
    signature = transaction.get('signature')
    sender = transaction.get('sender_address')
    if new_node.validate_transaction(transaction, signature, sender):
        response = 'success'
        return jsonify(response), 200
    else:
        response = 'error'
        return jsonify(response), 409

# Broadcast node ring to other nodes
@app.route('/broadcast/ring', methods=['POST'])
def broadcast_ring():
    message = request.get_json()
    #print(message)
    new_node.ring = json.loads(message)
    for node in new_node.ring:
        if node["public_key"]==new_node.public: new_node.id="id"+str(node["id"])
    response = 'success'
    return jsonify(response), 200


# Broadcast block to other nodes
@app.route('/broadcast/block', methods=['POST'])
def broadcast_block():
    # get json post
    block = json.loads(request.get_json())
    response = 0
    Thread(target=new_node.valid_block(block)).start()
    return jsonify(response), 200

# Register node to bootstrap ring
@app.route('/nodes/register', methods=['POST'])
def register_node():
    message = request.get_json()
    print(message)
    new_node.register_node_to_ring(message)
    response = 'success'
    return jsonify(response), 200

## Get current node's version of chain
#@app.route('/receive/chain', methods=['GET'])
#def get_chain():
#    return jsonify(new_node.blockchain.to_json()), 200

#@app.route('/broadcast/chain', methods=['POST'])
#def post_chain():
#    # Test, turn json into object
#    data = json.loads(request.get_json())
#    print(f'Current blockchain {new_node.blockchain}')
#    print(f'Popping last block to notice change')
#    print(f'{new_node.blockchain.blocks.pop()}')

#    print(f'Trying to update blocks in blockchain')

    # Replace wallet
    # Generate correct blocks in order to replace ones in the chain
#    blocks = [
#        Block(index=block["index"], transactions=[
#            Transaction(sender_address=t["sender_address"], receiver_address=t["receiver_address"],
#                        amount=t["amount"], transaction_inputs=t["transaction_inputs"],
#                        wallet=t["wallet"], ids=t["node_id"]) for t in block["transactions"]
#        ],
#              nonce=block["nonce"], previous_hash=block["previous_hash"], timestamp=block["timestamp"]) for block in
#        data["blockchain"]
#    ]

#    new_node.blockchain.blocks = blocks
#    print(f'new blockchain {new_node.blockchain}')

#    return 'Chain successfully updated!', 201

## Get current wallet
#@app.route('/receive/wallet', methods=['GET'])
#def get_wallet():
#    return jsonify(new_node.wallet.to_json()), 200

## Get current wallet
#@app.route('/broadcast/wallet', methods=['POST'])
#def post_wallet():
#    # Test, turn json into object
#    data = json.loads(request.get_json())

#    print(data)

#    wallet = Wallet(public_key=data["public_key"], private_key=data["private_key"], transactions=data["transactions"],
#                    utxos=data["utxos"], others_utxos=data["others_utxos"], value=data["value"])

#    print(wallet)

#    return 200

#----------------------------------------------------------------------#
#--------------------- RES API FOR FRONTEND --------------------------#
#----------------------------------------------------------------------#
# Home page
@app.route('/', methods=['GET'])
def home():
    # Keep track of current page
    session['viewing'] = 'home'
    # pass data to page call
    data = {
        'ADDRESS': new_node.address,
        'PUB_KEY': new_node.public,
        'NO_OF_NODES': len(new_node.ring),
        'CPU_PERCENT': psutil.cpu_percent(),
        'MEM_PERCENT': psutil.virtual_memory()[2]
    }
    return render_template('home.html', data=data)

# Node's Wallet
@app.route('/wallet', methods=['GET'])
def wallet():
    session['viewing'] = 'wallet'
    # pass data to page call
    data = {
        'NODE_ID': new_node.id,
        'ADDRESS': new_node.address,
        'BALANCE': new_node.wallet.wallet_balance(),
    }
    return render_template("wallet.html", data=data)

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

##############################################################################################

# Function to read file for transactions
def read_file(node, number_of_nodes):
    #print('Nop')
    while len(node.ring) < number_of_nodes:
        time.sleep(30)
        print('Nop')
        pass
    print("Reading file of transactions!")
    #print('\n\n\n\n',node.ring)
    print("./transactions/trans" + str(node.id[2:]) + ".txt")
    f = open("./transactions/trans" + str(node.id[2:]) + ".txt", "r")

    for line in f:
        time.sleep(1)
        node_id, value = (f.readline()).split()
        for nodes in node.ring:
            if nodes.get('id') == node_id[2:]:
                #print(nodes.get('id'))
                receiver = nodes.get("public_key")
                node.create_transaction(node.public, receiver, int(value))
                #Thread(target = node.create_transaction, args = (node.public, receiver, int(value),)).start()
                break
    print('My transactions finished!')

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
    # Read transactions file
    read_treans_thread = Thread(target=read_file, args=(new_node, no_of_nodes))
    read_treans_thread.start()

    #global new_node
    #new_node = Node(HOST, PORT, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes)
    #time.sleep(1)
    # Start Flask app
    from waitress import serve
    serve(app, host=HOST, port=PORT, threads=5) #, debug=True, use_reloader=False)
    #app.run(host=HOST, port=PORT, debug=False, use_reloader=False) #True
    #time.sleep(3)

    #t_app = Thread(target=start_new_flask_app, args=(HOST, PORT))
    #t_app.start()


