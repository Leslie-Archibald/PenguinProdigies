from flask import Flask, request, render_template, session, make_response,\
url_for, redirect
import flask
import os
from pymongo import MongoClient
from bson.json_util import dumps, loads
from flask_bcrypt import Bcrypt

import util.authentication as authentication
import util.constants as constants
from util.likes import *
from util.auction import *

app = Flask(__name__, template_folder='public')
bcrypt = Bcrypt(app)
client = MongoClient('localhost')
# client = MongoClient('mongo')
conn = client['cse312']
chat_collection = conn["chat"]
likes_collection = conn["likes"]
auction_collection = conn[constants.DB_AUCTION]


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
        return render_template('index.html', username=user, auctionPosts=auction_display_response(conn))
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
@app.route('/profilestyles.css')
def profile_css():
    myResponse = flask.send_from_directory('public', 'profilestyles.css')
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
    cookieName = "visits"
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
@app.route("/chat-message", methods = ['GET', "POST"])
def message_response():
    if request.method == "POST":
        myResponse = flask.make_response("Message Received")
        myResponse.headers['X-Content-Type-Options'] = 'nosniff'
        myResponse.mimetype = "text/plain; charset=utf-8"

        data = request.get_json(True)

        message = data["description"]
        message = message.replace("&", "&amp;")
        message = message.replace("<", "&lt;")
        message = message.replace(">", "&gt;")
        data["description"] = message

        title = data["title"]
        title = title.replace("&", "&amp;")
        title = title.replace("<", "&lt;")
        title = title.replace(">", "&gt;")
        data["title"] = title
        
        chat_collection.insert_one(data)
        print(data)
        return myResponse
@app.route("/chat-history", methods=['GET'])
def history_response():
    chat_cur = chat_collection.find({})
    temp = "["
    for chat in chat_cur:
        #print("Chat =")
        
        username = chat["username"]
        postID = chat["id"]
        chat["numLikes"] = numLikes(likes_collection, {"username":username,"id":postID} )
        #print(dumps(chat))
        temp += dumps(chat)
        temp += ", "
    temp = temp.strip(", ")
    temp += "]"
    json_data = temp
    print(json_data)
    response = flask.make_response(json_data.encode())
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = "applicaton/json; charset=utf-8"
    return response
@app.route("/like-message", methods=["POST"])
def like_response():
    print("Like recieved!")
    username = authentication.get_user(conn)
    postID = request.get_data(as_text=True)
    print("PostID is:", postID)
    totalLikes = likes(likes_collection,{"username":username,"id":postID} )
    return(history_response() )
@app.route('/profile')
def profile():
    response = make_response(render_template('profile.html'))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = "text/html"
    return response

@app.route('/auction-div', methods=['POST'])
def auction_Submit():
    return auction_submit_response(request, conn)

@app.route('/auction-add')
def auction_display():
    username = authentication.get_user(conn)
    auctionPosts = auction_display_response(conn)
    return redirect(url_for('user_Home', user=username))
    
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8080)
