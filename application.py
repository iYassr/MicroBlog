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
from flask import Flask, render_template, url_for, request, jsonify, redirect, Response, session as login_session

app = Flask(__name__)


@app.route('/')
@app.route('/blogs')
def main():
    return '<form method="GET"> <input type="text" name="name"> </input> <button type="submit">Submit </button> </form>'


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
    pass


@app.route('/blog/<int:id>/edit')
def edit_blog(id):
    pass


@app.route('/blog/<int:id>/delete')
def delete_blog():
    pass
