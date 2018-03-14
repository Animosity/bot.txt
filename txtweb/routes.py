from txtweb import txtweb, models
from flask import render_template

@txtweb.route('/')
def index():
    return render_template('index.html')

@txtweb.route('/articles.html')
def render_articles():
    return render_template('articles.html', articles=_get_articles())

@txtweb.route('/about.html')
def render_about():
    return render_template('about.html')

def _get_articles():
    query = models.Article.query.order_by(models.Article.id.desc()).limit(10)
    return query