import sqlite3

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    con = get_connection()
    try:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid
    finally:
        con.close()

def query(sql, params=[]):
    con = get_connection()
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()

