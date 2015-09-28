from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

class Recipients(Base):
    __tablename__ = 'recipients'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    birthday = Column(Date)
    
class Gifts(Base):
    __tablename__ = 'gifts'
    id = Column(Integer, primary_key=True)
    recipient_id = Column(Integer,ForeignKey('recipients.id'))
    description = Column(String(250))
    cost = Column(Integer)
    year = Column(Integer)
    holiday = Column(Integer) # 1 = Christmas, 2 = birthday

engine = create_engine('sqlite:///gifts.db')
Base.metadata.create_all(engine)
