import flask
from flask import make_response, render_template
import random
import util.constants as constants

# use of flask_bcrypt from https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/
def register(username, password, conn, bcrypt):
    db = conn[constants.DB_USERS]
    pass_encrypted = bcrypt.generate_password_hash(password)
    response = make_response(render_template('index.html', username=username))
    if db.find_one({'username': username}) != None:
        response = make_response(
            render_template('register.html', error='username taken')
            )
    # if cookieName in flask.request.cookies:
    #     return None
    else:
        auth = random.random()
        cookieName = constants.COOKIE_AUTH_TOKEN
        response.set_cookie(cookieName, auth, max_age=69420)
        db.insert_one({'username': username, 
                    'password': pass_encrypted, 
                    'auth': hash(auth)}
                    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = 'text/html; charset=utf-8; HttpOnly'
    return response

def login(username, password, db, bcrypt):
    user = db.find_one({'username': username})
    if user == None:
        return None
    pass_encrypted = user['password']
    is_valid = bcrypt.check_password_hash(pass_encrypted, password)
    if not is_valid:
        return None
    db.update_one({'username': username}, {})
    return True

def validate_user(authToken, db):
    user = db.find_one({'auth': hash(authToken)})
    if user == None:
        return None
    else:
        return user['username']
    
def auction(data, conn):
    print(data)
