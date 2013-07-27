#!/usr/bin/python
#coding=utf-8
import sys, os.path

sys.path.append(os.path.realpath('../'))

from flask.ext.script import Manager, prompt_bool
from app import app, db

manager = Manager(app)

@manager.command
def drop():
    """To drop all databases."""
    if prompt_bool('Are you sure to drop all the database. There is no return'):
        db.drop_all()

@manager.command
def create():
    """To create all databases."""
    db.create_all()

@manager.command
def recreate():
    """To reinstall all databases."""
    drop()
    create()

if __name__ == '__main__':
    manager.run()