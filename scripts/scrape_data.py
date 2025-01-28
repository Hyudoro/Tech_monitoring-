import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import logging
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

# Configure requests session with retries
session = requests.Session()
retry = Retry(
    total=3,  # Number of retries
    backoff_factor=1,  # Delay between retries
    status_forcelist=[403, 500, 502, 503, 504]  # Retry for these HTTP status codes
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Custom headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def scrape_data():
    # Define the database path
    db_path = os.path.join(os.path.dirname(__file__), '../db/tech_monitoring.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all sources from the database
    cursor.execute('SELECT id, url FROM sources')
    sources = cursor.fetchall()

    # Debug: Log fetched sources
    print(f"Fetched sources: {sources}")

    for source_id, url in sources:
        try:
            # Debug: Log current URL
            print(f"Processing source_id={source_id}, url={url}")

            # Check if URL has already been scraped
            cursor.execute('SELECT 1 FROM articles WHERE link = ?', (url,))
            if cursor.fetchone():
                print(f"URL already scraped, skipping: {url}")
                continue

            # Make the HTTP request
            response = session.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()  # Raise HTTP errors
            print(f"Request successful for: {url}")

            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the title
            title = soup.title.string.strip() if soup.title else "No Title"

            # Extract meta description (if available)
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'].strip() if meta_desc else "No Description"

            # Debug: Log scraped data
            print(f"Scraped data: title={title}, description={description}")

            # Insert scraped data into the database
            print(f"Inserting into database: source_id={source_id}, title='{title}', url='{url}', description='{description}'")
            cursor.execute('''
                INSERT INTO articles (source_id, title, link, summary, relevance)
                VALUES (?, ?, ?, ?, ?)
            ''', (source_id, title, url, description, "Pending Relevance"))

            print(f"Data inserted successfully for URL: {url}")

        except requests.exceptions.RequestException as e:
            error_message = f"HTTP error for {url}: {e}"
            logging.error(error_message)
            print(error_message)

        except Exception as e:
            error_message = f"Error scraping {url}: {e}"
            logging.error(error_message)
            print(error_message)

        # Random delay between requests
        sleep(randint(2, 5))

    # Commit changes and close the database connection
    conn.commit()
    conn.close()
    print("Scraping completed.")

if __name__ == "__main__":
    scrape_data()
