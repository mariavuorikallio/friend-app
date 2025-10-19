"""
Module for handling message threads and messages within threads in the Friend App.
"""

from datetime import datetime
import db


def get_threads_by_message(message_id):
    """Return all threads for a specific message."""
    sql = """
    SELECT t.id, t.user1_id, u1.username AS user1_name,
           t.user2_id, u2.username AS user2_name,
           t.ad_id
    FROM threads t
    JOIN users u1 ON t.user1_id = u1.id
    JOIN users u2 ON t.user2_id = u2.id
    WHERE t.ad_id = ?
    ORDER BY t.id DESC
    """
    return db.query(sql, [message_id])


def get_thread(thread_id):
    """Return a single thread by ID."""
    sql = """
    SELECT t.id, t.user1_id, t.user2_id, t.ad_id
    FROM threads t
    WHERE t.id = ?
    """
    result = db.query(sql, [thread_id])
    return result[0] if result else None


def get_user_threads(user_id):
    """Return all threads for a specific user."""
    sql = """
    SELECT t.id, t.ad_id,
           CASE
               WHEN t.user1_id = ? THEN u2.username
               ELSE u1.username
           END AS partner,
           m.title AS ad_title
    FROM threads t
    JOIN users u1 ON t.user1_id = u1.id
    JOIN users u2 ON t.user2_id = u2.id
    JOIN messages m ON t.ad_id = m.id
    WHERE t.user1_id = ? OR t.user2_id = ?
    ORDER BY t.id DESC
    """
    return db.query(sql, [user_id, user_id, user_id])


def get_messages(thread_id, _user_id=None):
    """Return messages in a thread for a user."""
    sql = """
    SELECT m.id, m.thread_id, m.sender_id, u.username AS sender_name, m.content, m.created_at
    FROM thread_messages m
    JOIN users u ON m.sender_id = u.id
    WHERE m.thread_id = ?
    ORDER BY m.created_at ASC
    """
    return db.query(sql, [thread_id])


def mark_thread_as_read(thread_id, user_id):
    """Mark all messages in a thread as read for the given user."""
    sql = """
    UPDATE thread_messages
    SET read_by_user = 1
    WHERE thread_id = ? AND sender_id != ?
    """
    db.execute(sql, [thread_id, user_id])


def get_or_create_thread(message_id, user_id, owner_id):
    """
    Return an existing thread ID for a message between two users,
    or create a new one if it does not exist.
    """
    sql = """
    SELECT id FROM threads
    WHERE ad_id = ? AND 
          ((user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?))
    """
    result = db.query(sql, [message_id, user_id, owner_id, owner_id, user_id])
    if result:
        return result[0][0]

    sql = "INSERT INTO threads (user1_id, user2_id, ad_id) VALUES (?, ?, ?)"
    thread_id = db.execute(sql, [user_id, owner_id, message_id])
    return thread_id


def send_message(thread_id, sender_id, content):
    """Send a message in a thread."""
    sql = """
    INSERT INTO thread_messages (thread_id, sender_id, content, created_at, read_by_user)
    VALUES (?, ?, ?, ?, 0)
    """
    db.execute(sql, [thread_id, sender_id, content, datetime.utcnow()])


