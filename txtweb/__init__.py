import os, sys, traceback
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


txtweb = Flask(__name__)
txtweb.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

from txtweb import routes
