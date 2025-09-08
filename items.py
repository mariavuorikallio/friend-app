import db

def add_item(title, description, age, user_id):
    sql = """INSERT INTO items (title, description, age, user_id) VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, age, user_id])
