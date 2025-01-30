from scrape_data import scrape_data
from summarize_and_evaluate import summarize_and_evaluate

def daily_update():
    scrape_data()
    summarize_and_evaluate()
    print("Daily update completed.")

if __name__ == "__main__":
    daily_update()
