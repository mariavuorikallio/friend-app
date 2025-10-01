CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE classes (
   id INTEGER PRIMARY KEY,
   title TEXT,
   value TEXT
);

CREATE TABLE messages (
   id INTEGER PRIMARY KEY,
   title TEXT,
   description TEXT,
   age INTEGER,
   user_id INTEGER REFERENCES users
);

CREATE TABLE message_classes (
    id INTEGER PRIMARY KEY,
    message_id INTEGER REFERENCES messages,
    title TEXT,
    value TEXT    
);

  
