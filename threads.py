import db

def get_or_create_thread(ad_id, user1_id, user2_id):
    """Palauttaa olemassa olevan keskustelun tai luo uuden."""
    sql = """SELECT id FROM threads 
             WHERE ad_id = ? 
               AND ((user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?))"""
    result = db.query(sql, [ad_id, user1_id, user2_id, user2_id, user1_id])
    if result:
        return result[0]["id"]

    sql = "INSERT INTO threads (ad_id, user1_id, user2_id) VALUES (?, ?, ?)"
    return db.execute(sql, [ad_id, user1_id, user2_id])


def get_messages(thread_id):
    """Palauttaa keskustelun viestit aikajärjestyksessä."""
    sql = """SELECT sender_id, content, created_at FROM thread_messages
             WHERE thread_id = ?
             ORDER BY created_at"""
    return db.query(sql, [thread_id])


def send_message(thread_id, sender_id, content):
    """Lisää viestin keskusteluun."""
    sql = "INSERT INTO thread_messages (thread_id, sender_id, content) VALUES (?, ?, ?)"
    db.execute(sql, [thread_id, sender_id, content])


def get_user_threads(user_id):
    """Hakee kaikki keskustelut, joissa käyttäjä on osallisena."""
    sql = """SELECT t.id, t.ad_id, m.title AS ad_title, u.username AS partner
             FROM threads t
             JOIN messages m ON t.ad_id = m.id
             JOIN users u ON (CASE WHEN t.user1_id = ? THEN t.user2_id ELSE t.user1_id END) = u.id
             WHERE t.user1_id = ? OR t.user2_id = ?
             ORDER BY t.created_at DESC"""
    return db.query(sql, [user_id, user_id, user_id])


def get_threads_by_message(ad_id):
    """Palauttaa kaikki threadit, jotka liittyvät tiettyyn ilmoitukseen/viestiin."""
    sql = """SELECT t.id, t.user1_id, t.user2_id, u1.username AS user1_name, u2.username AS user2_name
             FROM threads t
             JOIN users u1 ON t.user1_id = u1.id
             JOIN users u2 ON t.user2_id = u2.id
             WHERE t.ad_id = ?
             ORDER BY t.created_at DESC"""
    return db.query(sql, [ad_id])

