import os
import openai
import sqlite3
import time
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API Key not found. Make sure you have set an OPENAI_API_KEY in your .env file.")

# OpenAI client instance
client = openai.OpenAI(api_key=api_key)

def summarize_and_evaluate():
    with sqlite3.connect('../db/tech_monitoring.db') as conn:
        cursor = conn.cursor()

        # Fetch articles needing evaluation
        cursor.execute("SELECT id, title, link FROM articles WHERE relevance = 'Pending'")
        articles = cursor.fetchall()

        if not articles:
            print("No pending articles for evaluation.")
            return

        for article_id, title, link in articles:
            retries = 3  # Allow 3 retries for rate-limiting errors
            while retries > 0:
                try:
                    prompt = f"Summarize this article: {title} ({link}). Is this relevant for developers? Explain."
                    response = client.chat.completions.create(
                        model="gpt-4",  # Use GPT-4
                        messages=[
                            {"role": "system", "content": "You are an expert summarizer."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200  # Reduce token usage for cost efficiency
                    )
                    summary = response.choices[0].message.content.strip()
                    relevance = "Yes" if "yes" in summary.lower() else "No"

                    cursor.execute('''
                        UPDATE articles
                        SET summary = ?, relevance = ?
                        WHERE id = ?
                    ''', (summary, relevance, article_id))

                    print(f"✅ Article {article_id} summarized successfully.")
                    time.sleep(5)  # Small delay to avoid rate limits
                    break  # Exit retry loop if successful

                except openai.OpenAIError as e:
                    if "insufficient_quota" in str(e):
                        print(f"❌ API Quota Exceeded: {e}")
                        print("Check your OpenAI billing settings.")
                        return  # Stop execution
                    elif "rate limit" in str(e) or "429" in str(e):
                        print(f"⚠️ Rate limit exceeded for article {article_id}. Retrying in 30 seconds...")
                        time.sleep(30)  # Wait before retrying
                        retries -= 1
                    else:
                        print(f"❌ Unexpected error for article {article_id}: {e}")
                        break  # Stop retrying for unknown errors

        conn.commit()

if __name__ == "__main__":
    summarize_and_evaluate()
