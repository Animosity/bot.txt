import os, sys, traceback
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    db = SQLAlchemy(app)
    
