"""
This module contains functions related to thread management
and messages in threads for the friend-app project.
"""

import db
from flask import abort

def get_or_create_thread(ad_id, user1_id, user2_id):
    """Returns an existing thread or creates a new one."""
    sql = """SELECT id FROM threads 
             WHERE ad_id = ? 
               AND ((user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?))"""
    result = db.query(sql, [ad_id, user1_id, user2_id, user2_id, user1_id])
    if result:
        return result[0]["id"]

    sql = "INSERT INTO threads (ad_id, user1_id, user2_id) VALUES (?, ?, ?)"
    return db.execute(sql, [ad_id, user1_id, user2_id])

def user_in_thread(thread_id, user_id):
    """Checks if the user is a participant of the thread."""
    sql = "SELECT 1 FROM threads WHERE id = ? AND (user1_id = ? OR user2_id = ?)"
    result = db.query(sql, [thread_id, user_id, user_id])
    return bool(result)

def get_messages(thread_id, user_id):
    """Returns the messages of a thread in chronological order."""
    if not user_in_thread(thread_id, user_id):
        abort(403)
    sql = """
    SELECT tm.sender_id, u.username AS sender_name, tm.content, tm.created_at
    FROM thread_messages tm
    JOIN users u ON tm.sender_id = u.id
    WHERE tm.thread_id = ?
    ORDER BY tm.created_at
    """
    return db.query(sql, [thread_id])

def send_message(thread_id, sender_id, content):
    """Adds a message to a thread."""
    if not user_in_thread(thread_id, sender_id):
        abort(403)
    sql = "INSERT INTO thread_messages (thread_id, sender_id, content) VALUES (?, ?, ?)"
    db.execute(sql, [thread_id, sender_id, content])

def get_user_threads(user_id):
    """Retrieves all threads in which the user participates."""
    sql = """SELECT t.id, t.ad_id, m.title AS ad_title, u.username AS partner
             FROM threads t
             JOIN messages m ON t.ad_id = m.id
             JOIN users u ON (CASE WHEN t.user1_id = ? THEN t.user2_id ELSE t.user1_id END) = u.id
             WHERE t.user1_id = ? OR t.user2_id = ?
             ORDER BY t.created_at DESC"""
    return db.query(sql, [user_id, user_id, user_id])

def get_threads_by_message(ad_id):
    """Returns all threads related to a specific ad/message."""
    sql = """SELECT t.id, t.user1_id, t.user2_id, u1.username AS user1_name, u2.username AS user2_name
             FROM threads t
             JOIN users u1 ON t.user1_id = u1.id
             JOIN users u2 ON t.user2_id = u2.id
             WHERE t.ad_id = ?
             ORDER BY t.created_at DESC"""
    return db.query(sql, [ad_id])


def get_thread(thread_id):
    """Returns thread info, including the related ad/message ID."""
    sql = "SELECT id, ad_id, user1_id, user2_id FROM threads WHERE id = ?"
    result = db.query(sql, [thread_id])
    if not result:
        return None
    row = result[0]
    return {
        "id": row["id"],
        "ad_id": row["ad_id"],
        "user1_id": row["user1_id"],
        "user2_id": row["user2_id"]
    }
