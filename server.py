from flask import Flask, request, render_template, session, make_response, \
url_for
import flask
import os
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

import util.authentication as authentication
import util.constants as constants
import util.parse as parse

app = Flask(__name__, template_folder='public')
bcrypt = Bcrypt(app)
client = MongoClient('localhost')
conn = client['cse312']
upload_folder = 'public/images'
allowed_extensisons = {'png', 'jpg', 'jpeg'}

directory = directory = os.path.dirname(__file__)
#relative_Path = flask.Request.path
#relative_Path = relative_Path.strip("/")#removes leading "/" so that the paths will be joined properly

@app.route("/")
def home():
    # myResponse = flask.send_from_directory("public","index.html")
    cookieName = constants.COOKIE_AUTH_TOKEN
    if cookieName in flask.request.cookies:
        authToken = str(flask.request.cookies[cookieName])
        username = authentication.validate_user(authToken, conn, bcrypt)
    myResponse = make_response(render_template('index.html'))
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/html"
    return myResponse
@app.route("/style.css")
def home_css():
    myResponse = flask.send_from_directory("public","style.css")
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/css"
    return myResponse
@app.route("/formstyles.css")
def form_css():
    myResponse = flask.send_from_directory("public","style.css")
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/css"
    return myResponse


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
@app.route("/register")
def register():
    myResponse = flask.send_from_directory("public", "register.html")
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
    myResponse = flask.send_from_directory("public", "login.html")
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = 'text/html'
    return myResponse

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
def handle_multipart():
    buff = request._get_stream_for_parsing()
    buff = buff.read()
    boundary = "--" + request.headers["Content-Type"].split()[1].split('=')[1] + "\r\n"
    boundary = boundary.encode()

    data = parse.parse_multipart(buff, boundary)
    
    # token = request.cookies[constants.COOKIE_AUTH_TOKEN]
    # db = conn[constants.DB_USERS]
    # username = authentication.validate_user(token, db)
    # authentication.auction(data, conn)

    # auc_db = conn[constants.DB_AUC]

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8080)