"""
Tämä moduuli sisältää tietokantakyselyihin liittyvät yleiset funktiot.
"""

import sqlite3
from flask import g

def get_connection():
    """Palauttaa uuden SQLite-yhteyden ja asettaa foreign_keys päälle."""
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def execute(sql, params=None):
    """Suorittaa SQL-komennon ja palauttaa viimeksi lisätyn rivin ID:n."""
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
    """Suorittaa SQL-kyselyn ja palauttaa tulokset listana."""
    if params is None:
        params = []
    con = get_connection()
    try:
        rows = con.execute(sql, params).fetchall()
        return rows
    finally:
        con.close()

def last_insert_id():
    """Palauttaa viimeksi lisätyn rivin ID:n Flaskin g-objektista."""
    return getattr(g, "last_insert_id", None)

