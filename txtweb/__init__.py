import os, sys, traceback
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flaskext.markdown import Markdown
from flask_moment import Moment

txtweb = Flask(__name__)
txtweb.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(txtweb)
migrate = Migrate(txtweb, db)
moment = Moment(txtweb)
Markdown(txtweb)

from txtweb import routes, models

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    txtweb.run(host="0.0.0.0", port=port)
