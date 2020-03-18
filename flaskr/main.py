from flask import Flask, render_template
from flaskr.User import User
import os

from flaskr.breadcumb import breadcrumb

# Windows
# os.system('set FLASK_APP=main.py')

app = Flask(__name__, static_folder='static')
app.secret_key = "super secret key"

HOST = '127.0.0.1'
PORT = 5000

app.run(host=HOST, port=PORT)


@app.route('/')
@breadcrumb('home')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    # connection string to database (for user retrieval)
    conn = ''

    # Create instance of user, each user has a wallet attached to him
    # Each user has a unique id, should maybe implement a database to retrieve
    # based on login?!?!
    user = User(id=1, conn=conn)
    print(user)

