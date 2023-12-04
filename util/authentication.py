import flask
from flask import make_response, render_template, redirect, url_for
import random
import util.constants as constants
import hashlib

# use of flask_bcrypt from https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/
def register(username, password, email, conn, bcrypt):
    db = conn[constants.DB_USERS]
    print('------FORM DETAILS-------', username, password)
    pass_encrypted = bcrypt.generate_password_hash(password).decode()
    response = make_response(
    # code 303 is for redirects after POST requests
        # redirect(url_for('user_Home', user=username), code=307)
        redirect('/', code=307)
        )
    if db.find_one({'username': username}) != None:
        response = make_response(
            # redirect(url_for('register', error='username taken'), code=307)
            render_template('register.html', error='username taken')
            )
    # if cookieName in flask.request.cookies:
    #     return None
    else:
        auth = generate_auth_token(response)
        m = hashlib.sha256()
        m.update(auth.encode())
        db.insert_one({'username': username, 
                    'password': pass_encrypted, 
                    'auth': m.digest(),
                    'email': email,
                    'verified': False}
                    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = 'text/html; charset=utf-8'
    return response

def login(username, password, conn, bcrypt):
    db = conn[constants.DB_USERS]
    user = db.find_one({'username': username})
    if user == None:
        return None
    print(user)
    pass_encrypted = user['password']
    is_valid = bcrypt.check_password_hash(pass_encrypted, password)
    if not is_valid:
        return None
    response = make_response(
        redirect(url_for('user_Home', user=username), code=307)
        )
    auth = generate_auth_token(response)
    cookieName = constants.COOKIE_AUTH_TOKEN
    response.set_cookie(cookieName, auth, max_age=69420, httponly=True)
    m = hashlib.sha256()
    m.update(auth.encode())
    db.update_one({'username': username}, {"$set": {'auth': m.digest()}})
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = 'text/html; charset=utf-8'
    return response

def generate_auth_token(response):
    auth = str(random.random())
    cookieName = constants.COOKIE_AUTH_TOKEN
    response.set_cookie(cookieName, auth, max_age=69420)
    return auth

def get_user(conn):
    cookieName = constants.COOKIE_AUTH_TOKEN
    authToken = flask.request.cookies.get(cookieName)
    if authToken == None:
        return None
    db = conn[constants.DB_USERS]
    m = hashlib.sha256()
    m.update(authToken.encode())
    user = db.find_one({'auth': m.digest()})
    print(user)
    if user == None:
        return None
    else:
        return user['username']

def logout(conn, authToken):
    db = conn[constants.DB_USERS]
    response = make_response(redirect('/'))
    response.set_cookie('auth', '', max_age=0)
    db.update_one({'auth': hash(authToken)}, {"$pull": {'auth': hash(authToken)}})
    return response

def is_verified(user, conn):
    db = conn[constants.DB_USERS]
    cur = db.find_one({'username': user})
    if cur == None:
        return None
    else:
        return cur['verified']

def get_email(conn, user):
    db = conn[constants.DB_USERS]
    cur = db.find_one({'username': user})
    if cur == None:
        return None
    else:
        return cur['email']
