from pymongo import MongoClient


# use of flask_bcrypt from https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/
def register(username, password, db, bcrypt):
    pass_encrypted = bcrypt.generate_password_hash(password)
    if db.find_one({'username': username}) != None:
        return False
    db.insert_one({'username': username, 'password': pass_encrypted})
    return True

def login(username, password, db, bcrypt):
    user = db.find_one({'username': username})
    if user is None:
        return False
    pass_encrypted = user['password']
    is_valid = bcrypt.check_password_hash(pass_encrypted, password)
    if not is_valid:
        return False
    return True

