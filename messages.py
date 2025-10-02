import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)
    
    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)
       
    return classes
    
def add_message(title, description, age, user_id, classes):
    sql = """INSERT INTO messages (title, description, age, user_id) VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, age, user_id])
    
    message_id = db.last_insert_id()
    
    sql = "INSERT INTO message_classes (message_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [message_id, title, value])
 
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
                    users.id user_id,
                    users.username
             FROM messages, users
             WHERE messages.user_id = users.id AND
                   messages.id = ?"""
    result = db.query(sql, [message_id])
    return result[0] if result else None
     
def update_message(message_id, title, description, classes):
    sql = """UPDATE messages SET title = ?, description = ? WHERE id = ?"""
    db.execute(sql, [title, description, message_id])
    
    sql = "DELETE FROM message_classes WHERE message_id = ?"
    db.execute(sql, [message_id])
    
    sql = "INSERT INTO message_classes (message_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [message_id, title, value])    
    
def remove_message(message_id):
    sql = "DELETE FROM message_classes WHERE message_id = ?"
    db.execute(sql, [message_id])
    sql = "DELETE FROM messages WHERE id = ?"
    db.execute(sql, [message_id]) 
    
def find_messages(query):
    sql =  """SELECT id, title
              FROM messages
              WHERE title LIKE ? OR description LIKE ?
              ORDER BY id DESC""" 
    like = "%" + query + "%"
    return db.query(sql, [like, like])

            
