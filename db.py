"""
This module contains general functions related to database queries.
"""

import sqlite3
from flask import g

def get_connection():
    """Returns a new SQLite connection and enables foreign keys."""
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def execute(sql, params=None):
    """Executes an SQL command and returns the ID of the last inserted row."""
    if params is None:
        params = []
    con = get_connection()
    try:
        cur = con.execute(sql, params)
        con.commit()
        g.last_insert_id = cur.lastrowid 
        return cur.lastrowid
    finally:
        con.close()

def query(sql, params=None):
    """Executes an SQL query and returns the results as a list."""
    if params is None:
        params = []
    con = get_connection()
    try:
        rows = con.execute(sql, params).fetchall()
        return rows
    finally:
        con.close()

def last_insert_id():
    """Returns the ID of the last inserted row from the Flask g object."""
    return getattr(g, "last_insert_id", None)

