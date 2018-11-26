from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy.sql import func
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=True)
    username = Column(String(30), primary_key=True,  nullable=False)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    avatar = Column(String(250))
    bio = Column(String(250))
    phone_number = Column(String(14))
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'username': self.username,
            'bio': self.bio,
            'phone_number': self.phone_number,
            'email': self.email,
            'time_created': self.time_created,
        }


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey('user.id'))
    title = Column(String(250), nullable=False)
    content = Column(String(5000), nullable=False)
    type = Column(String(30))
    status = Column(String(30))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # Post can have many comments, while a comment can have only one post.
    # One to many
    #comment = relationship(Comment)
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'uid': self.uid,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'time_created': self.time_created,
            'time_updated': self.time_updated
        }


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True)
    pid = Column(Integer,  ForeignKey('post.id'), nullable=False)
    uid = Column(Integer, ForeignKey('user.id'), nullable=False)
    comment = Column(String(300), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class CommentLikes(Base):
    __tablename__ = 'comment_likes'
    id = Column(Integer, primary_key=True)
    cid = Column(Integer, ForeignKey('comment.id'), nullable=False)
    uid = Column(Integer, ForeignKey('user.id'))
    up_down = Column(String(4), nullable=False)


class PostLikes(Base):
    __tablename__ = 'post_likes'
    id = Column(Integer, primary_key=True)
    pid = Column(Integer, ForeignKey('post.id'), nullable=False)
    uid = Column(Integer, ForeignKey('user.id'))
    up_down = Column(String(4), nullable=False)


class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True, nullable=False)
    ip = Column(Integer, nullable=False)
    url = Column(String(300), nullable=False)
    response = Column(String(200))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'ip': self.ip,
            'url': self.url,
            'response': self.response,
        }


engine = create_engine('sqlite:///BlogDB.db')
Base.metadata.create_all(engine)
