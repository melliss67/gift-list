from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Recipients

engine = create_engine('sqlite:///gifts.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

d = date(1983, 1, 1)
rec1 = Recipients(name="Heather Webster",birthday=d)
session.add(rec1)

session.commit()
