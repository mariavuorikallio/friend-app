"""
Tämä moduuli sisältää foorumiviesteihin liittyvät funktiot.
"""

import db


def get_forum_messages(message_id):
    """Palauttaa kaikki foorumiviestit tietylle viestille."""
    sql = """SELECT r.id, r.content, r.sent_at, r.user_id, u.username
             FROM replies r, users u
             WHERE r.user_id = u.id AND r.message_id = ?
             ORDER BY r.id"""
    return db.query(sql, [message_id])


def add_forum_message(content, user_id, message_id):
    """Lisää uuden foorumiviestin tietylle viestille."""
    sql = """INSERT INTO replies (content, sent_at, user_id, message_id)
             VALUES (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, message_id])

