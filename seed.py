"""
Seed script for Friend App.
Creates test data for performance testing: users, threads, and messages.
"""

import random
import sqlite3
from werkzeug.security import generate_password_hash

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM threads")
db.execute("DELETE FROM messages")

user_count = 10
thread_count = 20
message_count = 50

print("Creating users...")
password = "test123" 
for i in range(1, user_count + 1):
    password_hash = generate_password_hash(password)
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        [f"user{i}", password_hash]
    )
db.commit()

print("Creating threads...")
for i in range(1, thread_count + 1):
    user1_id = random.randint(1, user_count)
    user2_id = random.randint(1, user_count)
    while user2_id == user1_id:
        user2_id = random.randint(1, user_count)
    ad_id = random.randint(1, message_count) 
    db.execute(
        "INSERT INTO threads (ad_id, user1_id, user2_id) VALUES (?, ?, ?)",
        [ad_id, user1_id, user2_id]
    )
db.commit()

print("Creating messages...")
for i in range(1, message_count + 1):
    user1_id = random.randint(1, user_count)
    user2_id = random.randint(1, user_count)
    while user2_id == user1_id:
        user2_id = random.randint(1, user_count)
    ad_id = random.randint(1, 10)  
    db.execute(
        "INSERT INTO threads (ad_id, user1_id, user2_id) VALUES (?, ?, ?)",
        [ad_id, user1_id, user2_id]
    )
db.commit()
 
db.commit()
db.close()
print("Seeding complete!")


