from pymongo import MongoClient
import flask
import random

# use of flask_bcrypt from https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/
def register(username, password, db, bcrypt):
    pass_encrypted = bcrypt.generate_password_hash(password)
    if db.find_one({'username': username}) != None:
        return None
    cookieName = 'auth'
    if cookieName in flask.request.cookies:
        return None
    auth = random.random()
    response = flask.make_response()
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = 'text/plain; charset=utf-8; HttpOnly'
    response.set_cookie(cookieName, auth, max_age=69420)
    db.insert_one({'username': username, 
                   'password': pass_encrypted, 
                   'auth': hash(auth)}
                   )
    return response

def login(username, password, db, bcrypt):
    user = db.find_one({'username': username})
    if user is None:
        return False
    pass_encrypted = user['password']
    is_valid = bcrypt.check_password_hash(pass_encrypted, password)
    if not is_valid:
        return False
    db.update_one({'username': username}, {})
    return True

