"""
This module contains functions related to message handling.
"""

import db
from flask import abort


def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, _ in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes


def add_message(message_title, description, age, user_id, classes):
    """Adds a new message to the database and associates it with classes."""
    sql = "INSERT INTO messages (title, description, age, user_id) VALUES (?, ?, ?, ?)"
    db.execute(sql, [message_title, description, age, user_id])

    message_id = db.last_insert_id() 

    sql = "INSERT INTO message_classes (message_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [message_id, class_title, class_value])


def get_classes(message_id):
    sql = "SELECT title, value FROM message_classes WHERE message_id = ?"
    return db.query(sql, [message_id])


def get_messages():
    sql = """SELECT messages.id,
                    messages.title,
                    messages.description,
                    messages.age,
                    users.username AS name
             FROM messages
             JOIN users ON messages.user_id = users.id
             ORDER BY messages.id DESC"""
    return db.query(sql)


def get_user_messages(user_id):
    sql = """SELECT DISTINCT m.id, m.title
             FROM messages m
             JOIN replies r ON r.message_id = m.id
             WHERE m.user_id = ?
             ORDER BY m.id DESC"""
    return db.query(sql, [user_id])


def get_message(message_id):
    sql = """SELECT messages.id,
                    messages.title,
                    messages.description,
                    messages.age,
                    users.id AS user_id,
                    users.username
             FROM messages
             JOIN users ON messages.user_id = users.id
             WHERE messages.id = ?"""
    result = db.query(sql, [message_id])
    return result[0] if result else None


def update_message(message_id, user_id, message_title, description, classes):
    """Updates a message's details and its associated classes."""
    message = get_message(message_id)
    if not message or message["user_id"] != user_id:
        abort(403)  # only owner can update

    sql = "UPDATE messages SET title = ?, description = ? WHERE id = ?"
    db.execute(sql, [message_title, description, message_id])

    sql = "DELETE FROM message_classes WHERE message_id = ?"
    db.execute(sql, [message_id])

    sql = "INSERT INTO message_classes (message_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [message_id, class_title, class_value])


def remove_message(message_id, user_id):
    """Deletes a message and its associated classes and threads safely."""
    message = get_message(message_id)
    if not message or message["user_id"] != user_id:
        abort(403)  
        
    sql = "DELETE FROM message_classes WHERE message_id = ?"
    db.execute(sql, [message_id])

    sql = "SELECT id FROM threads WHERE ad_id = ?"
    threads_list = db.query(sql, [message_id])
    for thread in threads_list:
        thread_id = thread["id"]
        db.execute("DELETE FROM thread_messages WHERE thread_id = ?", [thread_id])
        db.execute("DELETE FROM threads WHERE id = ?", [thread_id])

    sql = "DELETE FROM messages WHERE id = ?"
    db.execute(sql, [message_id])


def find_messages(query):
    sql = """SELECT id, title
             FROM messages
             WHERE title LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])

