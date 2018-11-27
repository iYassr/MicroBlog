'''
https://dba.stackexchange.com/questions/145222/structure-a-database-for-a-blog
'''
from flask import Flask, render_template, url_for, request, jsonify, redirect
from flask import Response, session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Post, Comment, CommentLikes, PostLikes, Log


app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///BlogDB.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/blogs')
def main():
    log('200')
    posts = session.query(Post).all()
    return render_template('index.html', posts=posts)


@app.route('/users')
def get_users():
    log('200')


@app.route('/user')
def get_user():
    log('200')


@app.route('/blog/<string:user>')
def get_user_blogs():
    pass


@app.route('/blog/new', methods=['GET', 'POST'])
def new_blog():
    if request.method == 'GET':
        log('200')
        return render_template('new_blog.html')
    if request.method == 'POST':
        log('302')
        uid = request.form.get('uid')
        title = request.form.get('title')
        content = request.form.get('content')
        new_post = Post(uid=1, title=title, content=content)
        session.add(new_post)
        session.commit()
        return redirect(url_for('main'))


@app.route('/blog/<int:post_id>/edit')
def edit_blog(post_id):
    pass


@app.route('/blog/<int:post_id>/delete')
def delete_blog(post_id):
    deleted_post = session.query(Post).filter_by(id=post_id).one()
    session.delete(deleted_post)
    session.commit()
    return redirect(url_for('main'))


@app.route('/login')
def login():
    pass


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
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
