

from flask import app, Flask, jsonify, request, render_template, make_response, session
import psutil

my_rest_api = Blueprint('my_rest_api', __name__)


# .......................................................................................
### REST API ###


# Home page
@app.route('/')
def home():
    # Store host ip and port
    session['HOST'] = HOST
    session['PORT'] = PORT
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
