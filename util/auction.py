import flask
import util.constants as const

import util.constants as constants
import util.authentication as auth
from flask import redirect, render_template, make_response
from werkzeug.utils import secure_filename
import time
import bcrypt

MONTHS={1:"January",2:"Febuary",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

def getAucInfo(id, conn):
    db = conn[const.DB_AUCTION]
    aucEntry = db.find_one({"auction id": id})

    if aucEntry == None:
        return {}
    else:
        return aucEntry
    #endIf
#endDef


def auction_submit_response(request, conn):
    auctiondb = conn[constants.DB_AUCTION]
    form = request.form
    endTime = int(time.time() + (int(form.get('time'))*60))
    username = auth.get_user(conn)

    cookieName = constants.COOKIE_AUTH_TOKEN
    authToken = request.cookies.get(cookieName)
    salt = bcrypt.gensalt()
    aucID = bcrypt.hashpw((str(time.time())+authToken).encode(),salt)[-10:-1]#takes the last 10 chars of the generated hash and uses that for the aucID
    print(aucID)

    ending = time.localtime(int(endTime))
    month = MONTHS.get(ending.tm_mon,"NULL")
    day = str(ending.tm_mday)
    hour = str(ending.tm_hour)
    minute = str(ending.tm_min)
    seconds = str(ending.tm_sec)
    timeStr = month + " " + day +", " +hour+":"+minute+":"+seconds

    #The end time is a time given in seconds since the last epoch. It indicates the end time of the auction. And we can derive the seconds remaining from that.
    db_insert_dict = {
        'title': form.get('title'),
        'description': form.get('description'),
        'auction id': aucID,
        'bid': form.get('bid'),
        'time': timeStr,
        'timeSeconds': endTime,
        'auction_owner': username,
        'image': request.files.get('upload').filename
    }
    file = request.files.get('upload')
    allowed_filetype = '.' in file.filename and \
        file.filename.split('.')[-1].lower() in constants.IMG_FILE_FORMATS

    if file is None or not allowed_filetype:
        return render_template('errormsg.html', msg='missing file field')
    for val in db_insert_dict.values():
        if val is None:
            return render_template('errormsg.html',
                                   msg='missing fields, unable to create auction')
    filename = secure_filename(file.filename)
    filename = f'{username}-{filename}'
    print('-----------filename--------', filename)
    file.save('./public/images/' + filename)
    db_insert_dict['image'] = '/images/' + filename

    auctiondb.insert_one(db_insert_dict)
    return redirect('/auction-add')

def auction_display_response(conn):
    auctiondb = conn[constants.DB_AUCTION]
    db_cursor = auctiondb.find({})
    display_fields = []
    for i in db_cursor:
        print(i['_id'])
        print('item in display_fields', i)
        display_fields.append(
            {'id': i.get('auction id'), 'title': i.get('title'), 'image': i.get('image'), 'description': i.get('description'), 'bid': i.get('bid'), 'winner': i.get('winner'), 'time': i.get('time')}
        )
            
    print('display_fields', display_fields)
    return display_fields

def auction_format(title, postID, description, imgPath, bid, winner, endTime):#NOT IN USE
    ending = time.localtime(int(endTime))
    month = MONTHS.get(ending.tm_mon,"NULL")
    day = str(ending.tm_mday)
    hour = str(ending.tm_hour)
    minute = str(ending.tm_min)
    seconds = str(ending.tm_sec)
    auctionHTML =  '<div class="auctionPost" id="' + postID  + '">'
    auctionHTML += '<hr>';
    auctionHTML += '<b>' + title + '</b>';
    auctionHTML += '<br />';
    auctionHTML += '<img class="auctionImage" src="' + imgPath + '" />';
    auctionHTML += '<p>' + description + '</p>'
    auctionHTML += '<p id="currBid">Current highest bid: ' + bid  + "</p>"
    auctionHTML += '<p id="currLeader">Current leader: ' + winner + '</p>';
    auctionHTML += '<p id="timer">Auction Ends: '+ month + " " + day +", " +hour+":"+minute+":"+seconds+'</p>';
    auctionHTML += '<label for="makeBid">' +\
            '<input id="makeBid" name="makeBid" type="text">' +\
            '</label>' +\
            '<button id="sendBid">Join Auction</button>' +\
            '<hr>' +\
            '</div>'
    return auctionHTML
