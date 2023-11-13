import util.constants as constants
from flask import redirect, render_template
from werkzeug.utils import secure_filename

def auction_response(request, conn):
    auctiondb = conn[constants.DB_AUCTION]
    form = request.form
    db_insert_dict = {
        'title': form.get('title'),
        'description': form.get('description'),
        'starting_bid': form.get('bid'),
        'time': form.get('time')
    }
    file = request.files.get('upload')
    allowed_filetype = file.filename.contains('.') and \
        file.filename.split('.')[-1].lower() in constants.IMG_FILE_FORMATS

    if file is None or not allowed_filetype:
        return render_template('errormsg.html', msg='missing file field')
    for val in db_insert_dict.values:
        if val is None:
            return render_template('errormsg.html',
                                   msg='missing fields, unable to create auction')
    filename = secure_filename(file.filename)


    auctiondb.insert_one()
