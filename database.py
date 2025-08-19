import sqlite3
from contextlib import closing

DATABASE = "scraper.db"

def init_db():
    """Initializes the database with a published_at column."""
    print("Initializing database with publication date support...")
    with closing(sqlite3.connect(DATABASE)) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS headlines (
                id INTEGER PRIMARY KEY,
                ticker TEXT NOT NULL,
                headline TEXT NOT NULL,
                source_url TEXT NOT NULL,
                published_at TEXT,
                sentiment_score REAL NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        db.commit()
    print("Database initialized.")

def add_headline(ticker: str, headline: str, url: str, published_at: str, sentiment: float):
    """Adds a new headline with its publication date."""
    with closing(sqlite3.connect(DATABASE)) as db:
        db.execute(
            "INSERT INTO headlines (ticker, headline, source_url, published_at, sentiment_score) VALUES (?, ?, ?, ?, ?)",
            (ticker, headline, url, published_at, sentiment)
        )
        db.commit()

def get_headlines(ticker: str):
    """Retrieves headlines and their metadata for a given ticker."""
    with closing(sqlite3.connect(DATABASE)) as db:
        cursor = db.execute(
            "SELECT headline, source_url, published_at, sentiment_score FROM headlines WHERE ticker = ? ORDER BY scraped_at DESC",
            (ticker,)
        )
        return [{"headline": row[0], "source_url": row[1], "published_at": row[2], "sentiment_score": row[3]} for row in cursor.fetchall()]

# --- THIS FUNCTION WAS MOVED TO THE CORRECT INDENTATION LEVEL ---
def get_sentiment_over_time(ticker: str):
    """
    Retrieves and averages sentiment scores by date for a given ticker.
    """
    with closing(sqlite3.connect(DATABASE)) as db:
        query = """
            SELECT
                date(published_at) as day,
                AVG(sentiment_score) as avg_sentiment
            FROM headlines
            WHERE ticker = ? AND published_at IS NOT NULL
            GROUP BY day
            ORDER BY day ASC;
        """
        cursor = db.execute(query, (ticker,))
        return [{"day": row[0], "avg_sentiment": row[1]} for row in cursor.fetchall()]