from flask import Flask, jsonify, request, render_template, make_response, session, Blueprint
from noobchain.main import app


blueprint = Blueprint('blockchain_views', __name__)


# View last transactions in the blockchain
@app.route('/transactions/view', methods=['GET'])
def get_transactions():
    # transactions = Blockchain.transactions
    response = 0  # {'transactions': transactions}
    return render_template("view_last_transactions.html")


# Show balance
@app.route('/show_balance', methods=['GET'])
def show_balance():
    # transactions = blockchain.transactions
    response = 0  # {'transactions': transactions}
    return render_template("show_balance.html")


# Create a transaction
@app.route('/transactions/create', methods=['POST'])
def create_transaction():
    message = request.get_json()
    response = 0
    return jsonify(response), 200


# Broadcast node ring to other nodes
@app.route('/broadcast/ring', methods=['POST'])
def broadcast_ring():
    message = request.get_json()
    response = 0
    return jsonify(response), 200


# Broadcast block to other nodes
@app.route('/broadcast/block', methods=['POST'])
def broadcast_block():
    message = request.get_json()
    response = 0
    return jsonify(response), 200

