import flask
import util.constants as const

import util.constants as constants
import util.authentication as auth
from flask import redirect, render_template, make_response
from werkzeug.utils import secure_filename
import time


def getAucInfo(id, conn):
    db = conn[const.DB_AUC]
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
    endTime = time.time() + (int(form.get('time'))*60)
    username = auth.get_user(conn)
    db_insert_dict = {
        'title': form.get('title'),
        'description': form.get('description'),
        'starting bid': form.get('bid'),
        'end time': form.get('time'),
        'auction owner': username,
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
        print('item in display_fields', i)
        display_fields.append(
            {'id': str(i['_id']), 'title': i['title'], 'image': i['image'], 'description': i['description'], 'bid': i.get('bid', ''), 'winner': i.get('winner', ''), 'time': i.get('time', '')}
        )
            
    print('display_fields', display_fields)
    return display_fields

def auction_format(title, postID, description, imgPath, bid, winner, time):
    auctionHTML =  '<div class="auctionPost" id="' + postID  + '">'
    auctionHTML += '<hr>';
    auctionHTML += '<b>' + title + '</b>';
    auctionHTML += '<br />';
    auctionHTML += '<img class="auctionImage" src="' + imgPath + '" />';
    auctionHTML += '<p>' + description + '</p>'
    auctionHTML += '<p id="currBid">Current highest bid: ' + bid  + "</p>"
    auctionHTML += '<p id="currLeader">Current leader: ' + winner + '</p>';
    auctionHTML += '<p id="timer">Time Remaining: '+ time + '</p>';
    auctionHTML += '<label for="makeBid">' +\
            '<input id="makeBid" name="makeBid" type="text">' +\
            '</label>' +\
            '<button id="sendBid">Send</button>' +\
            '<hr>' +\
            '</div>'
    return auctionHTML
