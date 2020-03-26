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
from flask_cors import CORS


app = Flask(__name__, static_folder='static')
app.secret_key = 'sec_key'
app.config['DEBUG'] = False
CORS(app)

app.config["CACHE_TYPE"] = "null"

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
#----------------------------------------------------------------------#
#---------------------- RES API FOR BACKEND ---------------------------#
#----------------------------------------------------------------------#

# View last transactions in the backend
#respond with our chain to resolve conflicts
@app.route('/chain', methods=['GET'])
def send_chain():
    chain = new_node.blockchain.to_json()
    return jsonify(chain), 200

@app.route('/transactions/view', methods=['GET'])
def get_transactions():
    # transactions = Blockchain.transactions
    response = 0  # {'transactions': transactions}
    return render_template("view_last_transactions.html")

# Create a transaction
@app.route('/transactions/create', methods=['POST'])
def create_browser_transaction():
    sender = request.form['sender_address']
    receiver = request.form['receiver_address']
    amount = request.form['amount']
    trans = new_node.create_transaction(sender, receiver, int(amount))
    response = 'success'
    return jsonify(response), 200

# Broadcast transaction
@app.route('/broadcast/transaction', methods=['POST'])
def create_transaction():
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
    new_node.register_node_to_ring(message)
    response = 'success'
    return jsonify(response), 200

# Show balance
#@app.route('/show_balance', methods=['GET'])
#def show_balance():
#    # transactions = backend.transactions
#    response = 0  # {'transactions': transactions}
#    return render_template("show_balance.html")

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
def read_file():
    print("Reading file for transactions")
    f = open("./transactions/trans" + str(new_node.id)[-1] + ".txt", "r")
    for j in range(5):
        node_id, value = (f.readline()).split()
        for nodes in new_node.ring:
            if nodes["id"] == node_id[2:]:
                receiver = nodes["public_key"]
                break    
        new_node.create_transaction(new_node.public ,receiver, int(value))
                #break
    return

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
    serve(app, host=HOST, port=PORT, threads=5)#, debug=True, use_reloader=False)
    #app.run(host=HOST, port=PORT, debug=False, use_reloader=False) #True
    #time.sleep(3)

    #t_app = Thread(target=start_new_flask_app, args=(HOST, PORT))
    #t_app.start()