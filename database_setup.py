from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    avatar = Column(String(250))
    bio = Column(String(250))
    phone_number = Column(String(14))


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    uid = Column(Integer, ForeignKey('user.id'))
    title = Column(String(250), nullable=False)
    content = Column(String(5000), nullable=False)
    type = Column(String(30))
    status = Column(String(30))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'uid': self.uid,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'time_created': self.time_created,
            'time_updated': self.time_updated
        }


class Log(Base):
    __tablename__ = 'menu_item'

    id = Column(Integer, primary_key=True)
    ip = Column(Integer, nullable=False)
    url = Column(String(300), nullable=False)
    response = Column(String(200), nullable=False)

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
