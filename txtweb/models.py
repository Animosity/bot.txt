from manage import db,app
from datetime import datetime
from txtweb import db

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(32), index=True, unique=True)
    discord_id = Column(db.String(128), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    avatar_uri = db.Column(db.String(256), index=False, unique=False)
    description = db.Column(db.String(1024), index=False, unique=False)
    posts =

    def __repr__(self):
        return '<Author %r>' % (self.nickname)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    discord_msg_id = db.Column(db.String(128), index=True, unique=True)
    post_date = db.Column('date', db.DateTime)
    title = db.Column('title', db.String(256))
    curators = relationship('Author', secondary='article_authors_assoc')
    content_markdown = db.Column('description', db.String(1024))

    def __repr__(self):
        return '<Article %r>' % (self.nickname)