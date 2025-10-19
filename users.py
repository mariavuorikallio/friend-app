"""
Module for handling user data and user profiles in the Friend App.
"""

import db
from werkzeug.security import generate_password_hash, check_password_hash


def get_user(user_id):
    """Return a single user by ID."""
    sql = "SELECT id, username, age, bio FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_messages(user_id):
    """Return all messages created by a specific user."""
    sql = """
    SELECT m.id, m.title, m.description
    FROM messages m
    WHERE m.user_id = ?
    ORDER BY m.id DESC
    """
    return db.query(sql, [user_id])


def create_user(username, password, age, bio):
    """Create a new user with a hashed password."""
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash, age, bio) VALUES (?, ?, ?, ?)"
    return db.execute(sql, [username, password_hash, age, bio])


def check_login(username, password):
    """Check user login credentials and return user ID if valid."""
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if result:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            return user_id
    return None


def update_profile(user_id, age, bio):
    """Update user's age and bio."""
    sql = "UPDATE users SET age = ?, bio = ? WHERE id = ?"
    db.execute(sql, [age, bio, user_id])


def update_image(user_id, image_data):
    """Update user's profile image."""
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image_data, user_id])


def get_image(user_id):
    """Return user's profile image."""
    sql = "SELECT image FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result and result[0][0] else None

