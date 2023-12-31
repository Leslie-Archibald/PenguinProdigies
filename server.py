from flask import Flask, request, render_template, session, make_response,\
url_for, redirect
import flask
import os
from pymongo import MongoClient
from bson.json_util import dumps, loads
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
import asyncio
import time

import util.authentication as authentication
import util.constants as constants
from util.likes import *
from util.auction import *
import json
import bson

app = Flask(__name__, template_folder='public')
bcrypt = Bcrypt(app)
client = MongoClient('localhost')
#client = MongoClient('mongo')
conn = client['cse312']
chat_collection = conn["chat"]
likes_collection = conn["likes"]
auction_collection = conn[constants.DB_AUCTION]

auctions_collection = conn["auctions"]
#auctions_collection.insert_one({"auction owner":"coolUser","title":"coolTitle","auction id":1234,"duration":"5","starting bid":"50","winning bid":""})

socket = SocketIO(app)


directory = directory = os.path.dirname(__file__)

@app.route("/", methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
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
@app.route("/joinAuc/<aucID>", methods=['GET', 'POST'])
def auction(aucID):
    item=getAucInfo(aucID,conn)
    servTitle=item.get("title","Title not found")
    servImg = item.get("image")
    servDesc=item.get("description","Description not found")
    servBid=item.get("bid","Highest bid could not be found")
    servWinner=item.get("winner","")

    myResponse = make_response(render_template('auctionBasic2.html', id=aucID, title=servTitle, image=servImg, description=servDesc, bid=servBid, winner=servWinner ) )
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
@app.route('/joinAuc/auctionFunctions.js')
def auctionFunctions_js():
    myResponse = flask.send_from_directory('public','auctionFunctions.js')
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/javascript"
    return myResponse
@app.route('/profilestyles.css')
def profile_css():
    myResponse = flask.send_from_directory('public', 'profilestyles.css')
    myResponse.headers['X-Content-Type-Options'] = 'nosniff'
    myResponse.mimetype = "text/css"
    return myResponse

@app.route("/joinAuc/functions.js")
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
@app.route("/cookie-counter")
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
@app.route("/chat-message", methods =["POST"])
def message_response():
    if request.method == "POST":
        print("hi")
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

        user = authentication.get_user(conn)
        if user != None:
            data["username"] = user
        
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
@app.route('/joinAuc/<path:aucID>/submitBid', methods=["POST"])
def submitBid(aucID):
    user = authentication.get_user(conn)
    auction = None
    response = flask.make_response("Failed")
    if(user != None):
        auction = auction_collection.find_one({"auction id":aucID})
        if(user == auction.get("auction_owner")):
            response = flask.make_response("Cannot make a bid on your auction")
            auction = None

    if(auction != None):
        currHighest = int(auction.get("bid","0"))
        userBid = request.get_data().decode().split("=")[1].strip()
        userBidInt = -1
        try:
            userBidInt = int(userBid)
            if( (int(auction.get("timeSeconds")) - int(time.time()) ) <= 0):
                response = flask.make_response("Auction Ended")
            elif(int(userBid) > currHighest):
                auction_collection.update_one({"auction id":aucID},{"$set":{"winner":user,"bid":userBid}})
                response = flask.make_response("Successful")
        except:
            response = flask.make_response("Only enter whole numbers for your bids")
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = "text/plain"

    return response

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ WebSocket Paths

@socket.on("connect")
def handleOpen():
    socket.emit("connect","1")

@socket.on("message")
def handleMsg(msg):
    socket.send(msg + " Also, LIGMA BAWLZ")

def startTimer(auctionID):
    #I dont think we need this
    totTime = int(time.time())+15

totTime = int(time.time()) + 60
@socket.on("getTime")
def giveTime():#auctionID
    #totTime = auctions_collection.find_one({"auction id":auctionID})["end time"]
    socket.emit('time-left',(totTime)-int(time.time()) )

@socket.on("getInfo")
def giveInfo(auctionID):
    info = getAucInfo(auctionID,conn)
    info["timeSeconds"] = str(int(info["timeSeconds"]) - int(time.time()))
    sendInfo = "{"
    for key in info.keys():
        if(key == "_id"):
            continue
        value = info[key]
        if(value == ""):
            value = "None"
        sendInfo += "\""+key+"\"" + ":"+"\""+value+"\""
        sendInfo +=","
    if(sendInfo[-1] == ","):
        #print("removed trailing ,")
        sendInfo = sendInfo[:-1]
    sendInfo += "}"
    #info = bson.decode(info)
    #print("Sent info the client: ",sendInfo,"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    socket.emit("info-response",sendInfo)

@socket.on("submitBid")
def submitBid(data):
    bidInfo = json.loads(data)
    print(data,"##############################################")
    print(bidInfo,"~~~~~~~~~~~~~~~~~~")
    currHighest = auctions_collection.find_one({"auction id":bidInfo["aucID"]}).get("winning bid","0")
    user = conn[constants.DB_USERS].find_one({"auth":bidInfo["auth"]})
    if(user == None):
        #invalid auth token, send client a "0"
        socket.emit("bid-response","0")
        return
    
    if(int(currHighest) < int(bidInfo["bidAmount"]) ):
        #update the DB and send the client a "1"
        socket.emit("bid-response","1")
        #WORK HERE!!!
        auction_collection.update_one({"auction id":bidInfo["aucID"]},{"$set":{"winner":user.get("username"),"bid":bidInfo["bidAmount"]}})

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
if __name__ == "__main__":
    #app.run(debug=True,host="0.0.0.0",port=8080)
    socket.run(app,host="0.0.0.0",port=8080,debug=True,allow_unsafe_werkzeug=True)
