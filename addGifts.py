from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Gifts

engine = create_engine('sqlite:///gifts.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

year = 2015
gift1 = Gifts(description="nothing",year=year,cost=0,recipient_id=2,holiday=1)
session.add(gift1)

gift2 = Gifts(description="book",year=year,cost=25,recipient_id=1,holiday=1)
session.add(gift2)

gift3 = Gifts(description="shirt",year=year,cost=12,recipient_id=3,holiday=1)
gift4 = Gifts(description="shoe",year=year,cost=10,recipient_id=3,holiday=1)
session.add(gift3)
session.add(gift4)

session.commit()
