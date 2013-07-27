#coding=utf-8
from datetime import datetime
from app import db

website_tech = db.Table(
    'website_tech',
    db.Column('website_id', db.Integer, db.ForeignKey('website.id')),
    db.Column('tech_id', db.Integer, db.ForeignKey('technology.id'))
)

class Website(db.Model):
    """Model for Website"""
    id              = db.Column(db.Integer, primary_key = True)
    hostname        = db.Column(db.String(1024), index = True)
    port            = db.Column(db.Integer, default = 80)
    title           = db.Column(db.String(1024), nullable = True, index = True)
    ipaddress       = db.Column(db.String(32), nullable = True)
    geo             = db.Column(db.String(128), nullable = True)
    frequency       = db.Column(db.Integer, default = 1)
    technologies    = db.relationship(
                                        'Technology',
                                        secondary   = website_tech, 
                                        backref     = db.backref('sites', lazy = 'dynamic')
                                    )
    create_time     = db.Column(db.DateTime, default = datetime.now())
    last_time       = db.Column(db.DateTime, default = datetime.now())

    def __repr__(self):
        return '<Website %r>' % (self.hostname)
        
class Technology(db.Model):
    """Model for Technology"""
    id              = db.Column(db.Integer, primary_key = True)
    category        = db.Column(db.String(16))
    title           = db.Column(db.String(128), nullable = False, index = True)
    detail          = db.Column(db.String(256), nullable = True, index = True)
    url             = db.Column(db.String(1024), nullable = True)

    def __repr__(self):
        return '<Technology %r>' % (self.title)

class Rule(db.Model):
    """Model for Rule"""
    id              = db.Column(db.Integer, primary_key = True)
    category        = db.Column(db.String(16))
    title           = db.Column(db.String(128), nullable = False, index = True)
    url             = db.Column(db.String(1024), nullable = True)
    match           = db.Column(db.String(128), nullable = True)
    regex           = db.Column(db.String(128), nullable = True)
    matchType       = db.Column(db.Integer, default = 1)
    nodeName        = db.Column(db.String(64), nullable = True)
    nodeAttributes  = db.Column(db.String(128), nullable = True)

    def __repr__(self):
        return '<Rule %r %r>' % (self.category, self.title)
        