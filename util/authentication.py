import flask
from flask import make_response, render_template, redirect, url_for
import random
import util.constants as constants

# use of flask_bcrypt from https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/
def register(username, password, conn, bcrypt):
    db = conn[constants.DB_USERS]
    print('------FORM DETAILS-------', username, password)
    pass_encrypted = bcrypt.generate_password_hash(password).decode()
    response = make_response(
    # code 303 is for redirects after POST requests
        redirect(url_for('user_Home', user=username), code=307)
        )
    if db.find_one({'username': username}) != None:
        response = make_response(
            render_template('register.html', error='username taken')
            )
    # if cookieName in flask.request.cookies:
    #     return None
    else:
        auth = generate_auth_token(response)
        db.insert_one({'username': username, 
                    'password': pass_encrypted, 
                    'auth': hash(auth)}
                    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = 'text/html; charset=utf-8; HttpOnly'
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
    db.update_one({'username': username}, {'auth': hash(auth)})
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = 'text/html; charset=utf-8; HttpOnly'
    return response

def generate_auth_token(response):
    auth = random.random()
    cookieName = constants.COOKIE_AUTH_TOKEN
    response.set_cookie(cookieName, str(auth), max_age=69420)
    return auth

def validate_user(authToken, conn):
    db = conn[constants.DB_USERS]
    user = db.find_one({'auth': hash(authToken)})
    if user == None:
        return None
    else:
        return user['username']