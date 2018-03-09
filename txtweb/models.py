from datetime import datetime
from txtweb import db


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(32), index=True, unique=True)
    discord_id = db.Column(db.String(128), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    avatar_uri = db.Column(db.String(256), index=False, unique=False)
    description = db.Column(db.String(1024), index=False, unique=False)
    posts = db.relationship('Article', backref='authors', lazy='dynamic')

    def __repr__(self):
        return '<Author %r>' % (self.nickname)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    discord_msg_id = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    title = db.Column('title', db.String(256))
    content_markdown = db.Column('description', db.String(1024))

    def __repr__(self):
        return '<Article %r>' % (self.title)

