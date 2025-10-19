"""
Module for handling messages and message classes in the Friend App.
"""

import db


def add_class_to_message(message_id, class_title, class_value):
    """Stub function for Pylint. Adds a class to a message in the database."""
    sql = "INSERT INTO message_classes (message_id, title, value) VALUES (?, ?, ?)"
    db.execute(sql, [message_id, class_title, class_value])


def get_messages():
    """Return all messages with basic info including user data."""
    sql = """
    SELECT m.id, m.title, m.description, m.user_id, u.username, u.age as user_age
    FROM messages m
    JOIN users u ON m.user_id = u.id
    ORDER BY m.id DESC
    """
    return db.query(sql)


def get_message(message_id):
    """Return a single message by ID."""
    sql = """
    SELECT m.id, m.title, m.description, m.user_id, u.username, u.age as user_age
    FROM messages m
    JOIN users u ON m.user_id = u.id
    WHERE m.id = ?
    """
    result = db.query(sql, [message_id])
    return result[0] if result else None


def add_message(title, description, age, user_id, classes_selected):
    """Add a new message with optional classes."""
    sql = "INSERT INTO messages (title, description, age, user_id) VALUES (?, ?, ?, ?)"
    message_id = db.execute(sql, [title, description, age, user_id])

    for class_title, class_value in classes_selected:
        add_class_to_message(message_id, class_title, class_value)

    return message_id


def update_message(message_id, user_id, title, description, classes_selected):
    """Update an existing message."""
    sql = "UPDATE messages SET title = ?, description = ? WHERE id = ? AND user_id = ?"
    db.execute(sql, [title, description, message_id, user_id])

    sql = "DELETE FROM message_classes WHERE message_id = ?"
    db.execute(sql, [message_id])

    for class_title, class_value in classes_selected:
        add_class_to_message(message_id, class_title, class_value)


def remove_message(message_id, user_id):
    """Remove a message by ID and its associated classes."""
    sql = "DELETE FROM message_classes WHERE message_id = ?"
    db.execute(sql, [message_id])
    
    threads_result = db.query("SELECT id FROM threads WHERE ad_id = ?", [message_id])
    for thread in threads_result:
        thread_id = thread[0]
        db.execute("DELETE FROM thread_messages WHERE thread_id = ?", [thread_id])
        db.execute("DELETE FROM threads WHERE id = ?", [thread_id])

    sql = "DELETE FROM messages WHERE id = ? AND user_id = ?"
    db.execute(sql, [message_id, user_id])


def get_all_classes():
    """Return all available message classes."""
    sql = "SELECT title, value FROM classes"
    result = db.query(sql)
    classes_dict = {}
    for title, value in result:
        if title not in classes_dict:
            classes_dict[title] = []
        classes_dict[title].append(value)
    return classes_dict


def get_classes(message_id):
    """Return classes for a specific message."""
    sql = "SELECT title, value FROM message_classes WHERE message_id = ?"
    result = db.query(sql, [message_id])
    return [{"title": title, "value": value} for title, value in result]


def find_messages(query):
    """Search messages by a substring in the title or description."""
    sql = "SELECT id, title FROM messages WHERE title LIKE ? OR description LIKE ? ORDER BY id DESC"
    q = f"%{query}%"
    return db.query(sql, [q, q])

