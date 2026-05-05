"""
This script initializes the SQLite database and creates the necessary tables 
for the Smart Attendance System.
Run this script once before starting the application.
"""
import sqlite3

# Connect to database (creates file if not exists)
conn = sqlite3.connect("database/attendance.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Create attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT,
    latitude REAL,
    longitude REAL,
    FOREIGN KEY(student_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("✅ Database and tables created successfully")
