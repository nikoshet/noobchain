# Import libraries
from flask import Flask, jsonify, request, render_template, make_response, session
from argparse import ArgumentParser
from threading import Thread
import time
import psutil

from noobchain.node.node import Node
from noobchain.rest_api import my_rest_api

app = Flask(__name__, static_folder='static')
app.secret_key = 'sec_key'
app.config['TESTING'] = True
app.register_blueprint(my_rest_api)

#HOST = '127.0.0.1'
#PORT = 4000


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
parser.add_argument('-ip_bootstrap', default='0.0.0.0', type=bool, help='ip of bootstrap')
parser.add_argument('-port_bootstrap', default=1000, type=bool, help='port of bootstrap')
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
# Save HOST, PORT as cookies
# res = make_response('Setting up Cookies')
# res.set_cookie('host', HOST)
# res.set_cookie('port', PORT)

print(f'Inputs: {HOST}, {PORT}, {boot}, {ip_of_bootstrap}, {port_of_bootstrap}, {capacity}, {difficulty}')
# Start node
t_node = Thread(target=start_new_node, args=(HOST, PORT, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes))
t_node.start()


if __name__ == '__main__':
    time.sleep(2)
    # connection string to database (for user retrieval)
    #conn = ''
    # Create instance of user, each user has a wallet attached to him
    #user = Node(id=1, conn=conn)
    #print(user)
    # Start Flask app
    app.run(host=HOST, port=PORT, debug=True)
