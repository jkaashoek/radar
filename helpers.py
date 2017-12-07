# Imports
from flask import redirect, render_template, request, session, g
from functools import wraps
import csv
import sqlite3

DATABASE = 'radar.db'

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Database code. Inspiration found in sqlite3 documentation.


def get_db():
    """Connects to sqllite3 database"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    """Handles database queries"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert(table, fields=(), values=()):
    """Handles database inserts"""
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    cur = get_db().execute(query, values)
    get_db().commit()
    id = cur.lastrowid
    cur.close()
    return id


def get_user(user_id):
    """Gets a user from database"""
    row = query_db("SELECT username FROM users WHERE id=?", [user_id], one=True)
    if row == None:
        return ''
    return row["username"]


def get_userrow(username):
    """Gets a user from database"""
    row = query_db("SELECT username FROM users WHERE username=?", [username], one=True)
    return row
