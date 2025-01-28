import sqlite3

def initialize_database():
    conn = sqlite3.connect('tech_monitoring.db')
    cursor = conn.cursor()

    # Create table for sources
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            category TEXT
        )
    ''')

    # Create table for scraped articles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            title TEXT,
            summary TEXT,
            link TEXT,
            relevance TEXT,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_id) REFERENCES sources (id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()