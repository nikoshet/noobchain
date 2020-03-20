from flask import Flask, jsonify, request, render_template, make_response, session, Blueprint
from noobchain.main import app, HOST, PORT
import psutil

blueprint = Blueprint('layout_views', __name__)


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
