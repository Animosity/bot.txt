from txtweb import txtweb
from flask import render_template

@txtweb.route('/')
def index():
    return render_template('index.html')