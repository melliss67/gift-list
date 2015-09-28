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

d2 = date(1969, 9, 3)
rec2 = Recipients(name="Rich Ellis",birthday=d2)
session.add(rec2)

d3 = date(1949, 12, 15)
rec3 = Recipients(name="Jo Ellis",birthday=d3)
session.add(rec3)

session.commit()
