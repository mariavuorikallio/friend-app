"""
This module contains functions and database queries related to users.
"""

from werkzeug.security import check_password_hash, generate_password_hash
import db


def get_user(user_id):
    """Returns user information by user ID, including whether the user has a profile image."""
    sql = """SELECT id, username, image IS NOT NULL AS has_image
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_messages(user_id): 
    """Returns the messages of a user.""" 
    sql = "SELECT id, title FROM messages WHERE user_id = ? ORDER BY id DESC" 
    return db.query(sql, [user_id])


def create_user(username, password, age=None, bio=None):
    """Creates a new user and hashes the password. Age and bio are optional."""
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash, age, bio) VALUES (?, ?, ?, ?)"
    user_id = db.execute(sql, [username, password_hash, age, bio])
    return user_id


def check_login(username, password):
    """Verifies a user's login credentials."""
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
    """Saves the user's profile image to the database."""
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image, user_id])


def get_image(user_id):
    """Retrieves the user's profile image from the database."""
    sql = "SELECT image FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0]["image"] if result else None


def update_profile(user_id, age=None, bio=None):
    sql = "UPDATE users SET age = ?, bio = ? WHERE id = ?"
    db.execute(sql, [age, bio, user_id])

