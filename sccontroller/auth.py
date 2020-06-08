import sqlite3
from . import db

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


def get_user(username):
    user = db.get_db().execute(
        'SELECT * FROM user WHERE username=?',
        (username, )
    ).fetchone()

    if user:
        return User(user['id'], user['username'], user['password'])
    else:
        return None


def get_user_by_id(id):
    user = db.get_db().execute(
        'SELECT * FROM user WHERE id=?',
        (id, )
    ).fetchone()

    if user:
        return User(user['id'], user['username'], user['password'])
    else:
        return None


def add_user(username, password):
    message = ""
    try:
        db.get_db().execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.get_db().commit()
        message = "User was successfully created"
    except Exception as err:
        message = err
    finally:
        return message


def del_user(username):
    message = ""
    try:
        db.get_db().execute(
            'DELETE FROM user WHERE username=?',
            (username, )
        )
        db.get_db().commit()
        message = "User was successfully deleted"
    except Exception as err:
        message = err
    finally:
        return message


@click.command('add-user')
@click.option('--username', prompt='Your username', help='Username for user to add')
@click.option('--passwd', prompt='Your password',
              help='Password for user to add')
@with_appcontext

def add_user_command(username, passwd):
    """Add new user"""
    click.echo(add_user(username, passwd))


@click.command('del-user')
@click.option('--username', prompt='Your username', help='Username for user to add')
@with_appcontext

def del_user_command(username):
    """Delete user"""
    click.echo(del_user(username))


def init_app(app):
    app.cli.add_command(add_user_command)
    app.cli.add_command(del_user_command)
