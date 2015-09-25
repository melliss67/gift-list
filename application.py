from flask import Flask, render_template
from werkzeug import secure_filename
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Users, Recipients

app = Flask(__name__)

engine = create_engine('sqlite:///gifts.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def hello_world():
    return 'It is working'

@app.route('/recipients')
def show_recipients():
    recipient_list = session.query(Recipients).all()
    return render_template('recipients.html', recipient_list = recipient_list)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
