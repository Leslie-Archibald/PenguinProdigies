from flask import Flask, request, render_template, session, make_response,\
url_for, redirect
import flask
import os
from pymongo import MongoClient
from bson.json_util import dumps, loads
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

import util.authentication as authentication
import util.constants as constants
from util.likes import *
import util.parse as parse


app = Flask(__name__, template_folder='public')
bcrypt = Bcrypt(app)
#client = MongoClient('localhost')
client = MongoClient('mongo')
conn = client['cse312']
chat_collection = conn["chat"]
likes_collection = conn["likes"]
auc_collection = conn[constants.DB_AUC]

upload_path = '../PenguinProdigies/public/images'

directory = directory = os.path.dirname(__file__)
#relative_Path = flask.Request.path
#relative_Path = relative_Path.strip("/")#removes leading "/" so that the paths will be joined properly

@app.route("/", methods=['GET', 'POST'])
def home():
    myResponse = make_response(render_template('index.html'))
    username = authentication.get_user(conn)
    print('----- this the username i got back from token --------', 
          username, 
          hash(flask.request.cookies.get(constants.COOKIE_AUTH_TOKEN)))
    if username != None:
        myResponse = make_response(
            redirect(url_for('user_Home', user=username))
            )
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/html"
    return myResponse
@app.route("/user/<user>", methods = ['GET', 'POST'])
def user_Home(user):
    if authentication.get_user(conn) == user:
        return render_template('index.html', username=user)
    else:
        return render_template('errormsg.html', 
                               msg='token not found --invalid access')

@app.route("/style.css")
def home_css():
    myResponse = flask.send_from_directory("public","style.css")
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/css"
    return myResponse
@app.route('/formstyles.css')
def form_css():
    myResponse = flask.send_from_directory('public', 'formstyles.css')
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/css"
    return myResponse

@app.route("/user/functions.js")
@app.route("/functions.js")
def home_js():
    myResponse = flask.send_from_directory("public","functions.js")
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/javascript"
    return myResponse
@app.route("/images/<path:path>")
def images(path):
    if(".jpg" in path):
        file_Type = "image/jpg"
    elif(".png" in path):
        file_Type = "image/png"
    else:
        file_Type = "text/plain"

    myResponse = flask.send_from_directory("public/images",path)
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = file_Type
    return myResponse
@app.route("/register", methods=['GET', 'POST'])
def register():
    myResponse = make_response(render_template('register.html'))
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = 'text/html'
    return myResponse
@app.route("/registeraction", methods = ["POST"])
def register_Action():
    username = request.form.get('username')
    password = request.form.get('password')
    myResponse = authentication.register(username, password, conn, bcrypt)
    if myResponse == None:
        # return render_template('register.html', known_user=True)
        return render_template('errormsg.html', msg='This username is already taken', redirect='/')
    else:
        return myResponse

@app.route("/login")
def login():
    # myResponse = flask.send_from_directory("public", "login.html")
    myResponse = make_response(render_template('login.html'))
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = 'text/html'
    return myResponse
@app.route("/loginaction", methods = ["POST"])
def login_Action():
    username = request.form.get('username')
    password = request.form.get('password')
    myResponse = authentication.login(username, password, conn, bcrypt)
    if myResponse == None:
        # return render_template('register.html', known_user=True)
        return render_template('login.html', error='incorrect username or password')
    else:
        return myResponse

@app.route('/logout')
def logout():
    resp = authentication.logout(conn, flask.request.cookies.get('auth'))
    return resp


@app.route("/visit-counter")
def visits_Counter():
    cookieName = constants.COOKIE_VISIT_COUNTER
    if cookieName in flask.request.cookies:
        #There is a visits cookie, so lets increment it by 1
        value = int(flask.request.cookies[cookieName])
        value += 1
        value = str(value)
    else:
        #No visits counter
        value = 1
        value = str(value)
    myResponse = flask.make_response("The visits cookie is at:"+value)
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/plain; charset=utf-8"
    myResponse.set_cookie(cookieName,value,max_age=3600)#3600 is 1 hour!
    return myResponse

@app.route("/auction-div", methods=['POST'])
def get_Multipart():
    
    username = authentication.get_user(conn)
    buff = request._get_stream_for_parsing()
    buff = buff.read()
    boundary = "--" + request.headers["Content-Type"].split()[1].split('=')[1] + "\r\n"
    boundary = boundary.encode()

    #Parses buffer for auction info
    data = parse.parse_multipart(buff, boundary)

    #Insert user info into auc database
    data['username'] = username
    auc_collection.insert_one(data)

    #Chh
    if data['filename'] =='' or data['datatype'] not in authentication.allowed_extensisons:
        return render_template('errormsg.html', msg='No selected image for auction item', redirect='/')
    if data['datatype'] not in authentication.allowed_extensisons:
        return render_template('errormsg.html', msg='File type is not allowed', redirect='/')
    else:
        filename = secure_filename(data['filename'])
        filename = data['username'] + filename + '.' + data['filetype']
        file = open(upload_path + '/' + filename, 'wb')
        file.write(data['upload'])
        file.close()
    
    return render_template('index.html', redirect='/')

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8080)