from flask import Flask, render_template, request
import hashlib
import time
import json
import requests
app = Flask(__name__)
production = False
clients = ['jitsi.meet.eqiad.wmflabs:4000']

def auth(password):
    time.sleep(2)
    with open('token', 'r') as f:
        ticketmaster_token = f.read()
    with open('salt', 'r') as f:
        salt = bytes(f.read(), 'utf-8')
    dk = hashlib.pbkdf2_hmac('sha256', bytes(password, 'utf-8'), salt, 100000)
    return dk.hex() == ticketmaster_token

@app.route("/")
def hello():
    return "Hello!"

@app.route("/create", methods=['GET'])
def create_user():
    return render_template('create.html')

@app.route("/create", methods=['POST'])
def create_user_post():
    if not auth(request.form['token'].strip()):
        return 'Not allowed'
    if production:
        for client in clients:
            requests.post(
                client + '/create',
                {
                    'user': request.form['user'],
                    'password': request.form['password']
                }
            )
        return
    with open('users_to_create.json', 'r') as f:
        users_to_create = json.loads(f.read())
    users_to_create.append({'user': request.form['user'], 'password': request.form['password']})
    with open('users_to_create.json', 'w') as f:
        f.write(json.dumps(users_to_create))
    return 'Done!'
if __name__ == "__main__":
    app.run(host='0.0.0.0')
