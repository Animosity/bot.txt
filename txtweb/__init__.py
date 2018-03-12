import os, sys, traceback
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flaskext.markdown import Markdown
from flask_moment import Moment
from micawber.providers import bootstrap_basic
from micawber.contrib.mcflask import add_oembed_filters

txtweb = Flask(__name__)
txtweb.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(txtweb)
migrate = Migrate(txtweb, db)
moment = Moment(txtweb)
Markdown(txtweb)
oembed_providers = bootstrap_basic()
add_oembed_filters(txtweb, oembed_providers)

from txtweb import routes, models

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(port)
    txtweb.run(host="0.0.0.0", port=port)
