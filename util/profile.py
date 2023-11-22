import util.constants as constants
import util.authentication as auth 
from flask import redirect, render_template, make_response

def display_winners(conn, username):
    auctiondb = conn[constants.DB_AUCTION]

    db_cursor = auctiondb.find({"winner" : username})

    display_fields = []
    for i in db_cursor: 
        display_fields.append({'id': str(i['_id']), 'title': i['title'], 'image': i['image'], 'description': i['description'], 'bid': i.get('bid', ''), 'winner': i.get('winner', ''), 'time': i.get('time', '')})
    #endFor 

    return display_fields
#endDef

def display_created(conn, username):
    auctiondb = conn[constants.DB_AUCTION]

    db_cursor = auctiondb.find({"auction owner" : username})

    display_fields = []
    for i in db_cursor: 
        display_fields.append({'id': str(i['_id']), 'title': i['title'], 'image': i['image'], 'description': i['description'], 'bid': i.get('bid', ''), 'winner': i.get('winner', ''), 'time': i.get('time', '')})
    #endFor 

    return display_fields
#endDef


def auction_format(title, postID, description, imgPath, bid, winner, time):
    auctionHTML = '<div class="auctionPost" id=""'
    return auctionHTML