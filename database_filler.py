#! /usr/bin/env python3
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Post, Log, Comment, CommentLikes, PostLikes


engine = create_engine('sqlite:///BlogDB.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


new_user = User(username='Yasserd9fasd9', name='Yasser', email='yaasserd99@gmaifl.com', avatar='a',
                password='P@$$w0rd', bio='CS Student', phone_number='05050109865')
session.add(new_user)
session.commit()

new_user = User(username='mohammed43299', name='mohammed', email='maohmamed@gmafil.com',
                password='P@$$w0rd', bio='Pentester ', phone_number='05143142341324')
session.add(new_user)
session.commit()


new_user = User(username='saadkhan', name='saafdasd', email='dasafdsfadsafsdf@gmail.com',
                password='P@$$w0rd', bio='Accountatn ', phone_number='+23423423')
session.add(new_user)
session.commit()


new_post = Post(uid=1, title='The raise of the empire',
                content='once upon a time, the persian emire raised upon light and one day it fell, it was unexpected', type='history', status='live')
session.add(new_post)
session.commit()

new_post = Post(uid=2, title='CHELSEA WON THE PRIMER LEAGUE',
                content='Chelsea won the title, AGAIN! YESS 3 Nill', type='Sports', status='live')
session.add(new_post)
session.commit()

new_post = Post(uid=1, title='HOW I FEEL AFTER A COLD SHOWER',
                content='I FEEL FREAKING PERFECT, IT MAKES ME WANT TO FLY', type='Health', status='live')
session.add(new_post)
session.commit()


new_comment = Comment(pid=1, uid=3, comment='History of lies!!!!')
session.add(new_comment)
session.commit()


new_comment = Comment(pid=1, uid=1, comment='Why, could you explain!!!!')
session.add(new_comment)
session.commit()


new_comment = Comment(pid=2, uid=3, comment='This is not doing me any good!')
session.add(new_comment)
session.commit()

new_comment = Comment(
    pid=3, uid=2, comment='What the heck are you saying? this doesnt help!')
session.add(new_comment)
session.commit()


new_post_like = PostLikes(pid=1, uid=1, up_down='up')
session.add(new_comment)
session.commit()


new_post_like = PostLikes(pid=1, uid=2, up_down='up')
session.add(new_comment)
session.commit()

new_post_like = PostLikes(pid=1, uid=3, up_down='up')
session.add(new_comment)
session.commit()

new_post_like = PostLikes(pid=2, uid=3, up_down='down')
session.add(new_comment)
session.commit()


new_post_like = PostLikes(pid=2, uid=3, up_down='down')
session.add(new_comment)
session.commit()
