import os, sys, traceback
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flaskext.markdown import Markdown

txtweb = Flask(__name__)
txtweb.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(txtweb)
migrate = Migrate(txtweb, db)
Markdown(txtweb)

from txtweb import routes, models
