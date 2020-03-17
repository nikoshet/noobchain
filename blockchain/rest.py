from flask import Flask, jsonify, render_template
from argparse import ArgumentParser
#from flask_cors import CORS
import time
# import blockchain
import node
#import threading
from threading import Thread

app = Flask(__name__)
#CORS(app)
# blockchain = Blockchain()

def start_new_node(ip, port, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes):
    print("New node")
    new_node = node.Node(ip, port, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes)



# .......................................................................................
# arguments
parser = ArgumentParser()
parser.add_argument('-ip', default='0.0.0.0', type=str, help='ip of node')
parser.add_argument('-p', '--port', default=1000, type=int, help='port to listen on')
parser.add_argument('-bootstrap', default=True, type=bool, help='is node bootstrap?')
parser.add_argument('-ip_of_bootstrap', default='0.0.0.0', type=bool, help='ip of bootstrap')
parser.add_argument('-port_of_bootstrap', default=1000, type=bool, help='port of bootstrap')
parser.add_argument('-nodes', default=5, type=int, help='number of nodes')
args = parser.parse_args()
ip = args.ip
port = args.port
boot = args.bootstrap
ip_of_bootstrap = args.ip_of_bootstrap
port_of_bootstrap = args.port_of_bootstrap
no_of_nodes = args.nodes
# app.run(host='0.0.0.0', port=port)
# app.run(host='127.0.0.1', port=port)
print("a")
print(ip, port, boot, ip_of_bootstrap, port_of_bootstrap)
# Start node
t2 = Thread(target=start_new_node, args=(ip, port, boot, ip_of_bootstrap, port_of_bootstrap, no_of_nodes))
t2.start()

@app.route('/')
def home():
    # return render_template("home.html")
    return 'Hey, we have Flask in a Docker container!'


# View last transactions in the blockchain
@app.route('/view_last_transactions', methods=['GET'])
def get_transactions():
    # transactions = blockchain.transactions
    response = 0  # {'transactions': transactions}
    #return render_template("view_last_transactions.html")
    return jsonify(response), 200


# Help
@app.route('/help', methods=['GET'])
def help():
    # transactions = blockchain.transactions
    response = 0  # {'transactions': transactions}
    #return render_template("help.html")
    return jsonify(response), 200


# Show balance
@app.route('/show_balance', methods=['GET'])
def show_balance():
    # transactions = blockchain.transactions
    response = 0  # {'transactions': transactions}
    #return render_template("show_balance.html")
    return jsonify(response), 200


# Run it once for every node


if __name__ == '__main__':
    time.sleep(3)
    #node = node.Node(ip, port, boot, ip_of_bootstrap, port_of_bootstrap)
    print("aaaaa")
    app.run(host=ip, port=port)#, debug=False)
    print("s")
