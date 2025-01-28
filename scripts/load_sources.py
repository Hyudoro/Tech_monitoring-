import sqlite3
import os

def load_sources(file_path):
    # Build an absolute path to the database file
    db_path = os.path.join(os.path.dirname(__file__), '../db/tech_monitoring.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(file_path, 'r') as file:
        for line in file:
            # Skip empty lines
            if not line.strip():
                continue
            try:
                # Split the line using ';' as the delimiter
                name, url = map(str.strip, line.split(';', 1))

                # Check if the URL already exists
                cursor.execute('SELECT 1 FROM sources WHERE url = ?', (url,))
                if cursor.fetchone():
                    print(f"Duplicate URL found, skipping: {url}")
                    continue

                # Insert the source if it's not a duplicate
                cursor.execute(
                    'INSERT INTO sources (name, url, category) VALUES (?, ?, ?)',
                    (name, url, 'General')
                )
            except ValueError:
                print(f"Invalid format in line: {line.strip()}")

    conn.commit()
    conn.close()
    print("Sources successfully added to the database.")

if __name__ == "__main__":
    # Build an absolute path to the sources.txt file
    file_path = os.path.join(os.path.dirname(__file__), '../data/sources.txt')
    load_sources(file_path)

