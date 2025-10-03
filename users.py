"""
Tämä moduuli sisältää käyttäjiin liittyvät funktiot ja tietokantakyselyt.
"""

from werkzeug.security import check_password_hash, generate_password_hash
import db


def get_user(user_id):
    """Palauttaa käyttäjän tiedot käyttäjä-ID:n perusteella, mukaan lukien tieto profiilikuvasta."""
    sql = """SELECT id, username, image IS NOT NULL AS has_image
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_messages(user_id):
    """Palauttaa käyttäjän viestit."""
    sql = "SELECT id, title FROM messages WHERE user_id = ? ORDER BY id DESC"
    return db.query(sql, [user_id])


def create_user(username, password):
    """Luo uuden käyttäjän ja hashkaa salasanan."""
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    user_id = db.execute(sql, [username, password_hash])
    return user_id


def check_login(username, password):
    """Tarkistaa käyttäjän kirjautumistiedot."""
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]
    if check_password_hash(password_hash, password):
        return user_id
    return None


def update_image(user_id, image):
    """Tallentaa käyttäjän profiilikuvan tietokantaan."""
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image, user_id])


def get_image(user_id):
    """Hakee käyttäjän profiilikuvan tietokannasta."""
    sql = "SELECT image FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0]["image"] if result else None


