# Import libraries
from flask import Flask, jsonify, render_template
from noobchain.Node import Node
from noobchain.breadcumb import breadcrumb
from argparse import ArgumentParser
from threading import Thread
import time
import os

# Windows
# os.system('set FLASK_APP=main.py')

app = Flask(__name__, static_folder='static')
app.secret_key = "super secret key"

#HOST = '127.0.0.1'
#PORT = 4000

# .......................................................................................
### REST API ###


# Home page
@app.route('/')
@breadcrumb('home')
def home():
    return render_template('home.html')


# Help
@app.route('/help', methods=['GET'])
def help():
    return render_template("help.html")


# About
@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html")


# View last transactions in the blockchain
@app.route('/view_last_transactions', methods=['GET'])
def get_transactions():
    # transactions = Blockchain.transactions
    response = 0  # {'transactions': transactions}
    #return jsonify(response), 200
    return render_template("view_last_transactions.html")


# Show balance
@app.route('/show_balance', methods=['GET'])
def show_balance():
    # transactions = blockchain.transactions
    response = 0  # {'transactions': transactions}
    #return jsonify(response), 200
    return render_template("show_balance.html")


# .......................................................................................
# Function for node
def start_new_node(ip, port, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes):
    print("New node")
    new_node = Node(ip, port, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes)


# Arguments
parser = ArgumentParser()
parser.add_argument('-ip', default='0.0.0.0', type=str, help='ip of node')
parser.add_argument('-p', '--port', default=1000, type=int, help='port to listen on')
parser.add_argument('-bootstrap', default=True, type=bool, help='is node bootstrap?')
parser.add_argument('-ip_of_bootstrap', default='0.0.0.0', type=bool, help='ip of bootstrap')
parser.add_argument('-port_of_bootstrap', default=1000, type=bool, help='port of bootstrap')
parser.add_argument('-nodes', default=5, type=int, help='number of nodes')
#args = parser.parse_args()
args, _ = parser.parse_known_args()
HOST = args.ip
PORT = args.port
boot = args.bootstrap
ip_of_bootstrap = args.ip_of_bootstrap
port_of_bootstrap = args.port_of_bootstrap
no_of_nodes = args.nodes

print('Inputs:', HOST, PORT, boot, ip_of_bootstrap, port_of_bootstrap)
# Start node
t_node = Thread(target=start_new_node, args=(HOST, PORT, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes))
t_node.start()


if __name__ == "main":#'__main__':
    time.sleep(2)
    # connection string to database (for user retrieval)
    #conn = ''
    # Create instance of user, each user has a wallet attached to him
    #user = Node(id=1, conn=conn)
    #print(user)
    # Start Flask app
    app.run(host=HOST, port=PORT)
