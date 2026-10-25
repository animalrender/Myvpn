#!/usr/bin/env python3
"""Create a tiny SQLite database so REA's inspect-sqlite-database has a target."""
import os
import sqlite3

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo.db")
if os.path.exists(path):
    os.remove(path)
conn = sqlite3.connect(path)
conn.executescript(
    """
    CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, email TEXT);
    CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), total REAL);
    INSERT INTO users(name, email) VALUES ('Ada','ada@example.com'), ('Linus','linus@example.com');
    INSERT INTO orders(user_id, total) VALUES (1,42.5), (2,99.0);
    """
)
conn.commit()
conn.close()
print(path)
