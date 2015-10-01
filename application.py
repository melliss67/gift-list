import os
import random
import json
import string
import requests
import httplib2
import datetime

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from flask import Flask, render_template, request, redirect
from flask import session as login_session, url_for, flash, make_response
from werkzeug import secure_filename
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Users, Recipients, Gifts

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']

app.secret_key = 'super_secret_key'
    
engine = create_engine('sqlite:///gifts.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/')
def hello_world():
    if not login_session.get('access_token'):
        return redirect(url_for('login'))
    else:
        return redirect(url_for('show_recipients'))
        
        
@app.route('/no_email')
def no_email():
    return render_template('no_email.html')


@app.route('/recipients')
def show_recipients():
    if not login_session.get('access_token'):
        return redirect(url_for('login'))
    else:
        recipient_list = session.query(Recipients).order_by(Recipients.name)
        return render_template('recipients.html', recipient_list = recipient_list)

    
@app.route('/recipient_gifts/<int:recipient_id>')
def getGiftsByRec(recipient_id):
    if not login_session.get('access_token'):
        return redirect(url_for('login'))
    else:
        recipient = session.query(Recipients).filter_by(id=recipient_id).one()
        gift_list = session.query(Gifts).filter_by(recipient_id=recipient_id).\
            order_by(Gifts.year, Gifts.holiday)
        return render_template('gifts_by_recipient.html', recipient = recipient,
        gift_list = gift_list)
        
        
@app.route('/recipient/new', methods=['GET', 'POST'])
def newRecipient():
    if request.method == 'POST':
        birthdayDate = datetime.datetime.strptime(request.form['birthday'], '%Y-%m-%d').date()
        newRecipient = Recipients(name=request.form['name'],
            birthday=birthdayDate)
        session.add(newRecipient)
        session.commit()
        return redirect(url_for('show_recipients'))
    else:
        return render_template('new_recipient.html', 
            access_token=login_session.get('access_token'))


@app.route('/gift/new/<int:recipient_id>', methods=['GET', 'POST'])
def newGift(recipient_id):
    if request.method == 'POST':
        #make sure holiday it selected
        selHoliday = request.form.get('holiday', '')
        if not selHoliday:
            values = {'year' : request.form['year'],
                'cost' : request.form['cost'], 
                'description' : request.form['description']}
            recipient = session.query(Recipients).filter_by(id=recipient_id).one()
            return render_template('new_gift.html', recipient=recipient,
              access_token=login_session.get('access_token'), 
              error='You must select a holiday.', values=values)
        else:
            newGift = Gifts(recipient_id=request.form['recipient_id'], 
              year=request.form['year'], holiday=request.form['holiday'], 
              cost=request.form['cost'], description=request.form['description'])
            session.add(newGift)
            session.commit()
            return redirect(url_for('getGiftsByRec', recipient_id = recipient_id))
    else:
        values = {}
        recipient = session.query(Recipients).filter_by(id=recipient_id).one()
        return render_template('new_gift.html', recipient=recipient,
            access_token=login_session.get('access_token'), values=values)


@app.route('/gift/edit/<int:recipient_id>/<int:gift_id>', methods=['GET', 'POST'])
def editGift(recipient_id, gift_id):
    if request.method == 'POST':
        gift = session.query(Gifts).filter_by(id=gift_id).one()
        gift.description = request.form['description']
        gift.year = request.form['year']
        gift.description = request.form['description']
        gift.holiday = request.form['holiday']
        gift.cost = request.form['cost']
        session.commit()
        return redirect(url_for('getGiftsByRec', recipient_id = recipient_id))
    else:
        recipient = session.query(Recipients).filter_by(id=recipient_id).one()
        gift = session.query(Gifts).filter_by(id=gift_id).one()
        if gift.holiday == 1:
            holiday_checked = [' checked ', '']
        else:
            holiday_checked = ['', ' checked ']
        return render_template('edit_gift.html', recipient=recipient, gift=gift,
            access_token=login_session.get('access_token'),
            holiday_checked=holiday_checked)


@app.route('/gift/remove/<int:recipient_id>/<int:gift_id>')
def removeGift(recipient_id, gift_id):
    gift = session.query(Gifts).filter_by(id=gift_id).one()
    session.delete(gift)
    session.commit()
    return redirect(url_for('getGiftsByRec', recipient_id = recipient_id))


@app.route('/recipient/edit/<int:recipient_id>', methods=['GET', 'POST'])
def editRecipient(recipient_id):
    if request.method == 'POST':
        recipient = session.query(Recipients).filter_by(id=recipient_id).one()
        recipient.name = request.form['name']
        birthdayDate = datetime.datetime.strptime(request.form['birthday'],\
            '%Y-%m-%d').date()
        recipient.birthday = birthdayDate
        session.commit()
        return redirect(url_for('show_recipients'))
    else:
        recipient = session.query(Recipients).filter_by(id=recipient_id).one()
        return render_template('edit_recipient.html', recipient=recipient,
            access_token=login_session.get('access_token'))
    
    
@app.route('/recipient/remove/<int:recipient_id>')
def removeRecipient(recipient_id):
    recipient = session.query(Recipients).filter_by(id=recipient_id).one()
    session.delete(recipient)
    session.commit()
    return redirect(url_for('show_recipients'))


@app.route('/holidays')
def showHolidays():
    holidays = session.query(Gifts).group_by(Gifts.year, Gifts.holiday).\
        order_by(Gifts.year, Gifts.holiday)
    return render_template('holidays.html', holidays=holidays)


@app.route('/holiday_gifts/<int:year>/<int:holiday_id>')
def holidayGifts(year, holiday_id):
    gifts = session.query(Recipients, Gifts).join(Gifts).\
        filter_by(year=year, holiday=holiday_id).\
        order_by(Recipients.name)
    return render_template('holiday_gifts.html', gifts=gifts)


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        # return credentials.access_token
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
            % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('\
            Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['access_token'] = access_token
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user email exists, if it doesn't reject the login
    user_id = getUserID(data["email"])
    if not user_id:
        response = make_response(
            json.dumps("Email address not found."), 401)
        print "Email address not found."
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += ' -webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
    
    
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['access_token']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # invalid token
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def logout():
    # only if signed in with Google Plus
    if not login_session.get('gplus_id') is None:
        gdisconnect()
    return redirect('/')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)


#OAuth info
#Client ID	470201349887-jeeep5c9kie0k0cc17sb2nf9j7fqghdh.apps.googleusercontent.com
#Client secret	M53XnIEX05nq7LJelvPB8TEE
#Creation date	Sep 29, 2015, 7:30:52 AM
