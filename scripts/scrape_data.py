import sqlite3
import os
import logging
import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from random import randint
from time import sleep

# Configure logging
log_path = os.path.join(os.path.dirname(__file__), '../logs/scrape_errors.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)  # Ensure logs folder exists

logging.basicConfig(
    filename=log_path,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a session using cloudscraper to bypass bot detection
session = cloudscraper.create_scraper()

# Retry mechanism
retry_strategy = Retry(
    total=5,  # Retries up to 5 times
    backoff_factor=2,  # Exponential backoff: 2s, 4s, 8s...
    status_forcelist=[500, 502, 503, 504, 403]  # Retry for these errors
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Dynamic User-Agent
ua = UserAgent()

def scrape_data():
    # Define the database path
    db_path = os.path.join(os.path.dirname(__file__), '../db/tech_monitoring.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all sources from the database
    cursor.execute('SELECT id, url FROM sources')
    sources = cursor.fetchall()

    print(f"Fetched sources: {sources}")

    for source_id, url in sources:
        try:
            print(f"Processing source_id={source_id}, url={url}")

            # Check if URL has already been scraped
            cursor.execute('SELECT 1 FROM articles WHERE link = ?', (url,))
            if cursor.fetchone():
                print(f"URL already scraped, skipping: {url}")
                continue

            # Set a random User-Agent for each request
            headers = {'User-Agent': ua.random}

            # Make the HTTP request
            response = session.get(url, headers=headers, timeout=15)
            response.raise_for_status()  # Raise HTTP errors

            # Skip 404 errors
            if response.status_code == 404:
                print(f"404 Not Found for URL: {url}, skipping...")
                continue

            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the title
            title = soup.title.string.strip() if soup.title else "No Title"

            print(f"Scraped data: title={title}")

            # Insert scraped data into the database with default summary and relevance
            print(f"Inserting into database: source_id={source_id}, title='{title}', url='{url}'")
            cursor.execute('''
                INSERT INTO articles (source_id, title, link, summary, relevance)
                VALUES (?, ?, ?, ?, ?)
            ''', (source_id, title, url, "Pending Summary", "Pending"))

            print(f"Data inserted successfully for URL: {url}")

        except Exception as e:
            error_message = f"Error processing {url}: {e}"
            logging.error(error_message)
            print(error_message)

        # Random delay to reduce rate-limiting risk
        sleep(randint(2, 5))

    conn.commit()
    conn.close()
    print("Scraping completed.")

if __name__ == "__main__":
    scrape_data()
