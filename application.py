'''
https://dba.stackexchange.com/questions/145222/structure-a-database-for-a-blog
'''

from flask import Flask, render_template, url_for, request, jsonify, redirect, flash
from flask import Response, session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from database_setup import Base, User, Post, Comment, CommentLikes, PostLikes, Log
from werkzeug import secure_filename
import logging
from os import path
from random import choice
import random
import string
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


app = Flask(__name__)
UPLOAD_FOLDER = path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
QUESTION_OF_THE_DAY = ['Why are we here?',
                       'Tell me about your day?', 'What is your future like?']


# Connect to Database and create database session
engine = create_engine('sqlite:///BlogDB.db', echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app.secret_key = 'imnotthatevel'


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "RankMyWriting"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        log('200')

        state = ''.join(random.choice(string.ascii_uppercase +
                                      string.digits) for x in range(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state)
    if request.method == 'POST':
        log('302')
        username = request.form.get('username').lower()
        password = request.form.get('password')

        user_exists = None
        try:
            user_exists = session.query(User).filter(
                func.lower(User.username) == func.lower(username), User.password == password).first()
        except:
            pass

        if user_exists:
            login_session['name'] = user_exists.username
            login_session['username'] = user_exists.username
            login_session['id'] = user_exists.id
            login_session['email'] = user_exists.email
            login_session['bio'] = user_exists.bio
            return redirect(url_for('main'))
        else:
            return 'wrong username or password'


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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
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
        return response

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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['avatar'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['avatar']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], username=login_session['username'], email=login_session[
                   'email'], avatar=login_session['avatar'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/')
@app.route('/blogs')
def main():
    log('200')
    posts = None
    try:
        posts = session.execute(
            'select post.title,post.time_created,post.content, post.id, user.name from post inner join user on post.uid=user.id left join post_likes on post_likes.pid = post.id').fetchall()
    except Exception:
        pass

    username = 'Incognito'
    if 'username' in login_session:
        username = login_session['username']
        email = login_session['email']
        # user_id = login_session['id']

    return render_template('index.html', posts=posts, username=username, question_of_the_day=choice(QUESTION_OF_THE_DAY))


@app.route('/<int:pid>')
@app.route('/post/<int:pid>')
def get_post(pid):
    log('200')
    post = None
    try:
        post = session.execute(
            'select post.title,post.time_created,post.content, post.id, user.name from post inner join user on post.uid=user.id left join post_likes on post_likes.pid = post.id where ').fetchall()
    except Exception:
        pass

    username = 'Incognito'
    if 'username' in login_session:
        username = login_session['username']
        email = login_session['email']
        user_id = login_session['id']

    return render_template('index.html', posts=posts, username=username, question_of_the_day=choice(QUESTION_OF_THE_DAY))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        log('200')
        return render_template('register.html')
    if request.method == 'POST':
        log('302')
        avatar = 'default'
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        bio = request.form.get('bio')
        phonenumber = request.form.get('phone_number')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if 'avatar' in request.files:
            file = request.files['avatar']
            file.save(path.join(app.config['UPLOAD_FOLDER'], username))
            avatar = username

        new_user = User(name=name, username=username, email=email,
                        bio=bio, phone_number=phonenumber, password=password1, avatar=avatar)
        session.add(new_user)
        session.commit()
        log('200')
        app.logger.info('username: {} , email {} , name {} , password {} , phone {}'.format(
            username, name, email, password1, phonenumber))

        return redirect(url_for('main'))


@app.route('/logoff', methods=['GET', 'POST'])
def logoff():
    access_token = login_session.get('access_token')
    [login_session.pop(key) for key in list(
        login_session.keys()) if key != '_flashes']
    if access_token is None:
        return 'youre not logged on'

    if 'username' in login_session:
        login_session.pop('username')
        [login_session.pop(key) for key in list(
            login_session.keys()) if key != '_flashes']
        return 'youve been logged off'

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    return 'youve been logged off'


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
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/users')
def get_users():
    log('200')
    users = session.query(User).all()
    return render_template('users.html', users=users)


@app.route('/user/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id)
    log('200')
    return 'to be implemented'


@app.route('/blog/<string:username>')
def get_user_blogs(username):
    posts = None
    try:
        posts = session.execute(
            'select * from post,user on post.uid=user.id where user.username="{}"'.format(username)).fetchall()
    except Exception:
        session.rollback()
    return render_template('index.html', posts=posts)


@app.route('/blog/new', methods=['GET', 'POST'])
def new_blog():
    if request.method == 'GET':
        log('200')
        return render_template('new_blog.html')
    if request.method == 'POST':
        log('302')

        if 'username' not in login_session:
            return redirect(url_for('login'))

        uid = login_session['id']
        title = request.form.get('title')
        content = request.form.get('content')
        new_post = Post(uid=uid, title=title, content=content)
        session.add(new_post)
        session.commit()
        return redirect(url_for('main'))


@app.route('/comment/<int:post_id>/new', methods=['GET', 'POST'])
def new_comment(post_id):
    if request.method == 'GET':
        log('200')
        return render_template('new_blog.html')
    if request.method == 'POST':
        log('302')
        if 'username' not in login_session:
            return redirect(url_for('login'))

        comment = request.form.get('comment')
        uid = login_session['id']
        new_comment = Comment(uid=uid, pid=post_id,  comment=comment)
        session.add(new_comment)
        session.commit()
        return redirect(url_for('main'))


@app.route('/blog/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_blog(post_id):
    if request.method == 'GET':
        log('200')
        old_post = session.query(Post).filter_by(id=post_id).first()
        return render_template('edit_blog.html', post=old_post)
    if request.method == 'POST':
        log('302')
        if 'username' not in login_session:
            return redirect(url_for('login'))

    post_creator = session.query(Post).filter_by(id=post_id).one()
    if login_session['id'] == post_creator.uid:
        uid = login_session['id']
        title = request.form.get('title')
        content = request.form.get('content')
        old_post = session.query(Post).filter_by(id=post_id).one()
        old_post.content = content
        old_post.title = title
        session.add(old_post)
        session.commit()
        return redirect(url_for('main'))
    else:
        return 'youre not allowed to edit other peoples posts'


@app.route('/blog/<int:post_id>/delete')
def delete_blog(post_id):
    log('302')
    post_creator = session.query(Post).filter_by(id=post_id).one()

    if 'username' not in login_session:
        return redirect(url_for('login'))
    if login_session['id'] == post_creator.uid:
        deleted_post = session.query(Post).filter_by(id=post_id).one()
        session.delete(deleted_post)
        session.commit()
    else:
        return 'you dont have the right to delete other users posts'

    return redirect(url_for('main'))


@app.errorhandler(404)
def page_not_found(e):
    log('404')
    return '404 {}'.format(e), 404


def log(response):
    ip = request.remote_addr
    url = request.url
    response = response
    new_log = Log(ip=ip, url=url, response=response)
    session.add(new_log)
    try:
        session.commit()
    except:
        session.rollback()
        raise
