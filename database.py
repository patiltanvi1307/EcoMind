import sqlite3

connection = sqlite3.connect("ecomind.db")
cursor = connection.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    points INTEGER DEFAULT 0
)
""")

# Challenges table
cursor.execute("""
CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    challenge TEXT NOT NULL,
    completed_date TEXT NOT NULL
)
""")

connection.commit()
connection.close()

print("EcoMind database created successfully! 🌱")