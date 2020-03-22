from flask import Flask, jsonify, request, render_template, make_response, session, Blueprint
#from noobchain.main import app
import json
from collections import OrderedDict

blueprint = Blueprint('blockchain_views', __name__)


# View last transactions in the backend
@blueprint.route('/transactions/view', methods=['GET'])
def get_transactions():
    # transactions = Blockchain.transactions
    response = 0  # {'transactions': transactions}
    return render_template("view_last_transactions.html")


# Show balance
@blueprint.route('/show_balance', methods=['GET'])
def show_balance():
    # transactions = backend.transactions
    response = 0  # {'transactions': transactions}
    return render_template("show_balance.html")


# Create a transaction
@blueprint.route('/transactions/create', methods=['POST'])
def create_transaction():
    message = request.get_json()
    response = 0
    return jsonify(response), 200


# Broadcast node ring to other nodes
@blueprint.route('/broadcast/ring', methods=['POST'])
def broadcast_ring():
    message = request.get_json()
    response = 0
    return jsonify(response), 200


# Broadcast block to other nodes
#@app.route('/broadcast/block/<int:node_id>', methods=['POST'])
#def broadcast_block(node_id):
@blueprint.route('/broadcast/block/', methods=['POST'])
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

import sys, os
#sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(0,'..')
#print(sys.path.insert(1, os.path.join(sys.path[0], '..')))
#from backend.node import Node
#from main import new_node
#from __main__ import *
#from __main__ import new_node
import main
# Register node to bootstrap ring
@blueprint.route('/nodes/register', methods=['POST'])
def register_node():
    message = request.get_json()
    print(message)
    main.new_node.register_node_to_ring(message)
    response = 'success'
    return jsonify(response), 200