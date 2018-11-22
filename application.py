'''
users 
id
username 
name
email
avatar
bio
phonenumber 

posts
id
uid
title
content
time
image
type
status

logs
ip 
url
timestamp 

https://dba.stackexchange.com/questions/145222/structure-a-database-for-a-blog



'''
from flask import Flask, render_template, url_for, request, jsonify, redirect
from flask import Response, session as login_session


app = Flask(__name__)

users = [{'name': 'Yasser', 'id': '1',
          'username': 'yasserd99', 'email': 'Yasserd99@gmial.com'}, {'name': 'Fisal', 'id': '2',
                                                                     'username': 'Faisal2', 'email': 'faisal@gmial.com'}]


user = {'name': 'Yasser', 'id': '1',
        'username': 'yasserd99', 'email': 'Yasserd99@gmial.com'}

post = {'id': '1', 'uid': '1', 'title': 'How to wake up early',
        'content': 'to wake up early you need to to many things, like setting up the alarm clock, forming an intention to wake up early, cold shower, oh never mind', 'type': 'productivity', 'status': 'available',  'time': '21/Nov/2018'}
posts = [post, post, post]


@app.route('/')
@app.route('/blogs')
def main():
    return render_template('index.html', ip=request.remote_addr, id=10, posts=posts)


@app.route('/users')
def get_users():
    pass


@app.route('/user')
def get_user():
    pass


@app.route('/blog/<string:user>')
def get_user_blogs():
    pass


@app.route('/blog/new')
def new_blog():
    return render_template('new_blog.html')


@app.route('/blog/<int:blog_id>/edit')
def edit_blog(id):
    pass


@app.route('/blog/<int:blog_id>/delete')
def delete_blog():
    pass


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

        app.logger.info('username: {} , email {} , name {} , password {} , phone {}'.format(
            username, name, email, password1, phonenumber))
        return 'user created'
