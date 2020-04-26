import hashlib
import json
import time
from secrets import token_hex

import requests
from flask import Flask, render_template, request

app = Flask(__name__)
clients = ['http://jitsi.meet.eqiad.wmflabs:4000']
tokens_file = 'tokens.json'


def auth_ticketmaster(password):
    time.sleep(2)
    with open('token', 'r') as f:
        ticketmaster_token = f.read().strip()
    with open('salt', 'r') as f:
        salt = bytes(f.read(), 'utf-8')
    dk = hashlib.pbkdf2_hmac('sha256', bytes(password, 'utf-8'), salt, 100000)
    return dk.hex() == ticketmaster_token


def auth_token(token):
    time.sleep(2)
    with open(tokens_file, 'r') as f:
        tokens = json.loads(f.read())
    if token not in tokens:
        return False
    tokens.remove(token)
    with open(tokens_file, 'w') as f:
        f.write(json.dumps(tokens))
    return True


def gen_token():
    with open(tokens_file, 'r') as f:
        tokens = json.loads(f.read())
    token = token_hex(32)
    tokens.append(token)
    with open(tokens_file, 'w') as f:
        f.write(json.dumps(tokens))
    return token


@app.route("/")
def hello():
    return "Hello!"


@app.route("/generate_token", methods=['GET'])
def generate_token():
    return render_template('generate.html')


@app.route("/generate_token", methods=['POST'])
def generate_token_post():
    if not auth_ticketmaster(request.form['token'].strip()):
        time.sleep(10)
        return 'Not allowed'
    return gen_token()


@app.route("/create", methods=['GET'])
def create_user():
    return render_template('create.html')


@app.route("/create", methods=['POST'])
def create_user_post():
    if not auth_token(request.form['token'].strip()):
        time.sleep(10)
        return 'Not allowed'
    for client in clients:
        requests.post(
            client + '/create',
            {
                'user': request.form['user'],
                'password': request.form['password']
            }
        )
    return 'Done!'


if __name__ == "__main__":
    app.run(host='0.0.0.0')
