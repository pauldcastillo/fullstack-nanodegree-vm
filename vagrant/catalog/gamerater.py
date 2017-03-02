from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Game, UsersGames, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Gamerater"

# Create database
engine = create_engine('sqlite:///favoritegames.db')
Base.metadata.create_all(engine)

# Create database connector
DBSession = sessionmaker(bind = engine)
session = DBSession()

# Methods used
methods = ['GET', 'POST']

# Helper functions
def get_user_by_id(user_id):
    """Function for getting a user object given the user id."""
    return session.query(User).filter_by(id = user_id).one()

def get_user_id_by_email(email):
    """
    Function for getting the user id for the given email. If the user
    id cannot be found, returns None.
    """
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

def make_json_response(message, code):
    """
    Returns a json response with the given message and code.

    response = make_json_response("Invalid state", 401)
    """
    response = make_response(json.dumps(message), code)
    response.headers['Content-Type'] = 'application/json'
    return response

def create_user(login_session):
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    return get_user_id_by_email(login_session['email'])

def login_or_create_user(login_session):
    """See if user exists, and create the user."""
    user_id = get_user_id_by_email(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius: '
               '150px;-webkit-border-radius: 150px;-moz-border-radius: '
               '150px;"> ')
    return output



@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Logs the user in using Google third party authentication."""

    if request.args.get('state') != login_session['state']:
        return make_json_response('Invalid state parameter', 401)
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return make_json_response(
            'Failed to upgrade the authorization code', 401)

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % (
        access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        return make_json_response(result.get('error'), 500)

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        message = "Token's user ID doesn't match given user ID."
        return make_json_response(message, 401)

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        message = "Token's client ID does not match app's."
        print message
        return make_json_response(message, 401)

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return make_json_response('Current user is already connected.', 200)

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt' : 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # See if user exists, and create the user if not.
    output = login_or_create_user(login_session)
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route("/gdisconnect")
def gdisconnect():
    """
    Disconnects a logged in user. Should only be used with
    a connected user.
    """
    credentials = login_session.get('credentials')
    if credentials is None:
        return make_json_response("Current user not connected.", 401)

    # Execute HTTP GET request to revoke current token.
    access_token = credentials.access_token
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s' % (
        access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        return make_json_response('Successfully disconnected.', 200)
    else:
        # For whatever reason, the given token was invalid.
        return make_json_response(
            'Failed to revoke token for given user.', 400)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        return make_json_response('Invalid sate parameter', 401)
    access_token = request.data

    # Exchange client token for long-lived server-side token with GET
    # /oauth/access_token?grant_type=fb_exchange_token&client_id=
    # {app-id}&client_secret={app-secret}&fb_exchange_token=
    # {short-lived-token}
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id='
           '%s&client_secret=%s&fb_exchange_token=%s' % (
            app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # Strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    #print "url sent for API access: %s" % url
    #print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['provider'] = 'facebook'

    # Get user picture
    url = ('https://graph.facebook.com/v2.4/me/picture?%s&redirect=0'
           '&height=100&width=100' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data['data']['url']

    # See if user exists, and create the user if not.
    output = login_or_create_user(login_session)
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/fbdisconnect/')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

@app.route('/disconnect/')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('gamerater_home'))
    else:
        flash("You were not logged in to begin with!")
        redirect(url_for('gamerater_home'))

@app.route('/login/')
def show_login():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/')
@app.route('/gamerater/')
def gamerater_home():
    return render_template("home.html")

@app.route('/gamerater/popular/')
def gamerater_popular():
    return render_template("popular.html")

@app.route('/gamerater/game/<int:game_id>/')
def game_info(game_id):
    return render_template("game.html")

@app.route('/gamerater/user/<int:user_id>/')
def user_info(user_id):
    return render_template("user.html")

@app.route('/gamerater/add-game')
def add_game():
    return "This is where you will add a game."

@app.route('/gamerater/rate-game')
def rate_game(game_id=None):
    return render_template("rate_game.html", game_id=game_id)

@app.route('/gamerater/my-games')
def my_games():
    return 'This is where the user will be able to see their own games.'

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)