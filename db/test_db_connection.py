import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'tech_monitoring.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, url FROM sources')
    sources = cursor.fetchall()
    print(f"Fetched sources: {sources}")
    conn.close()
except sqlite3.Error as e:
    print(f"Database error: {e}")
