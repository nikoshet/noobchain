# Import libraries
import psutil
import requests
from flask import Flask, render_template, request, jsonify, session
from argparse import ArgumentParser
from threading import Thread
import time
import json
from backend.node import Node
from datetime import datetime
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'sec_key'
app.config['DEBUG'] = False
CORS(app)

# Arguments
parser = ArgumentParser()
#parser.add_argument('-ip', default='0.0.0.0', type=str, help='ip of node')
parser.add_argument('-ip', default='127.0.0.1', type=str, help='ip of node')
parser.add_argument('-p', '--port', default=1000, type=int, help='port to listen on')
parser.add_argument('-bootstrap', default='False', type=str, help='is node bootstrap?')
#parser.add_argument('-ip_bootstrap', default='0.0.0.0', type=str, help='ip of bootstrap')
parser.add_argument('-ip_bootstrap', default='127.0.0.1', type=str, help='ip of bootstrap')
parser.add_argument('-port_bootstrap', default=1000, type=int, help='port of bootstrap')
parser.add_argument('-nodes', default=3, type=int, help='number of nodes')
parser.add_argument('-cap', default=5, type=int, help='capacity of blocks')
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

# Start node
new_node = Node(HOST, PORT, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes, capacity, difficulty)

######################################################################
# ------------------------------------------------------------------ #
# ---------------------- REST API FOR BACKEND ---------------------- #
# ------------------------------------------------------------------ #
######################################################################


# Respond with our chain to resolve conflicts
@app.route('/chain', methods=['GET'])
def send_chain():
    chain = new_node.blockchain.to_json()
    return jsonify(chain), 200


# View transactions from last verified block
@app.route('/transactions/view', methods=['GET'])
def get_transactions():
    last_bl_trans = new_node.blockchain.blocks[-1].to_json()
    ax = json.loads(last_bl_trans)
    trans = ax['transactions']
    return jsonify(trans), 200


# Get money sent from verified transactions
@app.route('/transactions/money/sent', methods=['GET'])
def get_money_sent():
    value = 0
    for blk in new_node.blockchain.blocks:
        blk = json.loads(blk.to_json())
        trans = blk['transactions']
        for tr in trans:
            if tr['sender_address'] == new_node.public:
                value += tr['amount']
    return jsonify(value), 200


# Get money received from verified transactions
@app.route('/transactions/money/received', methods=['GET'])
def get_money_received():
    value = 0
    for blk in new_node.blockchain.blocks:
        blk = json.loads(blk.to_json())
        trans = blk['transactions']
        for tr in trans:
            if tr['receiver_address'] == new_node.public:
                value += tr['amount']
    return jsonify(value), 200


# Create a transaction on frontend
@app.route('/transactions/create/browser', methods=['POST'])
def create_browser_transaction():
    sender = str(request.form['sender_address'])
    sender = sender.replace(' ', '\n')
    sender = '-----BEGIN PUBLIC KEY-----\n' + sender + '\n-----END PUBLIC KEY-----'
    receiver = str(request.form['receiver_address'])
    receiver = receiver.replace(' ', '\n')
    receiver = '-----BEGIN PUBLIC KEY-----\n' + receiver + '\n-----END PUBLIC KEY-----'
    amount = request.form['amount']

    if not amount.isnumeric():
        response = 'The amount of NBCs is not valid.'
        return jsonify(response), 400

    elif sender == receiver:
        response = 'Sender public key is the same with the receiver public key.'
        return jsonify(response), 400

    elif new_node.public != sender:
        response = 'This is not your public key.'
        return jsonify(response), 400

    elif sender != new_node.public:
        response = 'Your public key is not valid.'
        return jsonify(response), 400

    else:
        for node in new_node.ring:
            if node["public_key"] == receiver:
                trans = new_node.create_transaction(sender, receiver, int(amount))
                response = 'success'
                return jsonify(response), 200
        response = 'The public key of receiver is not valid.'
        return jsonify(response), 400


# Create a transaction
@app.route('/transactions/create', methods=['POST'])
def create_transaction():
    trans = json.loads(request.get_json())
    sender = trans['sender_address']
    receiver = trans['receiver_address']
    amount = trans['amount']
    for node in new_node.ring:
        if node["id"] == sender[2:]: sender = node["public_key"]
        if node["id"] == receiver[2:]: receiver = node["public_key"]
    time.sleep(0.5)
    new_node.create_transaction(sender, receiver, int(amount))
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
    new_node.ring = json.loads(message)
    for node in new_node.ring:
        if node["public_key"] == new_node.public:
            new_node.id="id"+str(node["id"])
            my_path = os.path.abspath(os.path.dirname(__file__))
            with open(os.path.join(my_path, "./public_keys/key"+str(node["id"])+".txt"), "w") as key_file:
                key_file.write(new_node.public)
    response = 'success'
    return jsonify(response), 200


# Broadcast block to other nodes
@app.route('/broadcast/block', methods=['POST'])
def broadcast_block():
    # get json post
    block = json.loads(request.get_json())
    response = 0
    new_node.valid_block(block)

    return jsonify(response), 200


# Register node to bootstrap ring
@app.route('/nodes/register', methods=['POST'])
def register_node():
    message = request.get_json()
    print(message)
    new_node.register_node_to_ring(message)
    response = 'success'
    return jsonify(response), 200

#####################################################################
# ----------------------------------------------------------------- #
# --------------------- RESΤ API FOR FRONTEND --------------------- #
# ----------------------------------------------------------------- #
#####################################################################


# Home page
@app.route('/', methods=['GET'])
def home():
    # Keep track of current page
    session['viewing'] = 'home'
    data = {
        'ADDRESS': new_node.address,
        'PUB_KEY': new_node.public.replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', ''),
        'NO_OF_NODES': len(new_node.ring),
        'CPU_PERCENT': psutil.cpu_percent(),
        'MEM_PERCENT': psutil.virtual_memory()[2]
    }
    return render_template('home.html', data=data)


# Node's Wallet
@app.route('/wallet', methods=['GET'])
def wallet():
    session['viewing'] = 'wallet'
    money_sent = requests.get(new_node.address + '/transactions/money/sent').json()
    money_received = requests.get(new_node.address + '/transactions/money/received').json()
    date = json.loads(new_node.blockchain.blocks[-1].to_json())['timestamp']
    date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'NODE_ID': new_node.id,
        'ADDRESS': new_node.address,
        'BALANCE': new_node.wallet.wallet_balance(),
        'BLOCK_INDEX': json.loads(new_node.blockchain.blocks[-1].to_json())['index'],
        'BLOCK_NONCE': json.loads(new_node.blockchain.blocks[-1].to_json())['nonce'],
        'MONEY_SENT': money_sent,
        'MONEY_RECEIVED': money_received,
        'BLOCK_DATETIME': date,
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


# Current Blockchain
@app.route('/blockchain', methods=['GET'])
def blockchain():
    session['viewing'] = 'blockchain'
    return render_template("blockchain.html", data=new_node.blockchain.to_od_with_hash())


# Custom filter to convert UNIX time to HUMAN TIME
@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s)


if __name__ == '__main__':

    print(f'\nHost\'s IP: {HOST}, Host\'s Port: {PORT}, Bootstrap Node: {boot}')
    print(f'Boostrap\'s IP: {ip_of_bootstrap}, Boostrap\'s Port: {port_of_bootstrap}')
    print(f'Nodes in the network: {no_of_nodes}, Block\'s Capacity: {capacity}, Mining Difficulty: {difficulty}\n')

    # Start Flask app
    from waitress import serve
    serve(app, host=HOST, port=PORT, threads=10)
