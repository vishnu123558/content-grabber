import sqlite3
import os
from datetime import datetime

DB_PATH = "storage/database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def file_exists(url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE url = ?", (url,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def insert_file_metadata(url, filename, file_type):
    if file_exists(url):
        print(f"⚠️ File already exists in DB: {url}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO files (url, filename, file_type, timestamp) VALUES (?, ?, ?, ?)", 
                   (url, filename, file_type, timestamp))
    conn.commit()
    conn.close()
    print(f"✅ Added to database: {filename}")

if __name__ == "__main__":
    init_db()

    