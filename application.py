'''
https://dba.stackexchange.com/questions/145222/structure-a-database-for-a-blog
'''

from flask import Flask, render_template, url_for, request, jsonify, redirect
from flask import Response, session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Post, Comment, CommentLikes, PostLikes, Log
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///BlogDB.db', echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app.secret_key = 'imnotthatevel'


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
        user_id = login_session['id']

    return render_template('index.html', posts=posts, username=username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        log('200')
        return render_template('register.html')
    if request.method == 'POST':
        log('302')
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        bio = request.form.get('bio')
        phonenumber = request.form.get('phonenumber')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        new_user = User(name=name, username=username, email=email,
                        bio=bio, phone_number=phonenumber, password=password1)
        session.add(new_user)
        session.commit()
        log('200')
        app.logger.info('username: {} , email {} , name {} , password {} , phone {}'.format(
            username, name, email, password1, phonenumber))

        return redirect(url_for('main'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        log('200')
        return render_template('login.html')
    if request.method == 'POST':
        log('302')
        username = request.form.get('username')
        password = request.form.get('password')

        user_exists = None
        try:
            user_exists = session.query(User).filter_by(
                username=username, password=password).one()
        except:
            pass

        if user_exists:
            login_session['username'] = user_exists.username
            login_session['id'] = user_exists.id
            login_session['email'] = user_exists.email
            login_session['bio'] = user_exists.bio
            return redirect(url_for('main'))
        else:
            return 'wrong username or password'


@app.route('/logoff', methods=['GET', 'POST'])
def logoff():
    if request.method == 'GET':
        log('302')
        if 'username' in login_session:
            login_session.pop('username')
            return 'youve been logged off'
        else:
            return 'youre not logged on'


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


# todo
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

        uid = login_session['id']
        title = request.form.get('title')
        content = request.form.get('content')
        old_post = session.query(Post).filter_by(id=post_id).one()
        old_post.content = content
        old_post.title = title
        session.add(old_post)
        session.commit()
        return redirect(url_for('main'))


@app.route('/blog/<int:post_id>/delete')
def delete_blog(post_id):
    log('302')
    deleted_post = session.query(Post).filter_by(id=post_id).one()
    session.delete(deleted_post)
    session.commit()
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
