from flask import Flask, request, render_template, session, make_response, url_for, redirect
import flask
from flask import request
import os
from pymongo import MongoClient
from bson.json_util import dumps, loads
from util.likes import *
import json

app = Flask(__name__)

directory = directory = os.path.dirname(__file__)
#relative_Path = flask.Request.path
#relative_Path = relative_Path.strip("/")#removes leading "/" so that the paths will be joined properly

app = Flask(__name__, template_folder='public')
# client = MongoClient('mongo')
mongo_client = MongoClient("localhost")
db = mongo_client["cse312"]
chat_collection = db["chat"]
likes_collection = db["likes"]

@app.route("/")
def home():
    myResponse = make_response(render_template('index.html'))
    #myResponse = flask.send_from_directory("public","index.html")
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/html"
    return myResponse
@app.route("/style.css")
def home_css():
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
@app.route("/chat-message", methods=['POST'])
def meesage_response():
    if request.method == "POST":
        myResponse = flask.make_response("Message Received")
        myResponse.headers['X-Content-Type-Options'] = 'nosniff'
        myResponse.mimetype = "text/plain; charset=utf-8"
        mongo_client = MongoClient("localhost")
        db = mongo_client["cse312"]
        chat_collection = db["chat"]
        data = request.get_json(True)
        chat_collection.insert_one(data)
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
    #print(json_data)
    response = flask.make_response(json_data.encode())
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = "applicaton/json; charset=utf-8"
    return response
@app.route("/like-message", methods=["POST"])
def like_response():
    print("Like recieved!")
    username = "Guest"
    postID = request.get_data(as_text=True)
    print("PostID is:", postID)
    totalLikes = likes(likes_collection,{"username":username,"id":postID} )
    return(history_response() )

    
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8080)