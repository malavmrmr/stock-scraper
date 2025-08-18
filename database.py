import sqlite3
from contextlib import closing

DATABASE = "scraper.db"

def init_db():
    """Initializes the database with an upgraded headlines table."""
    print("Initializing database with sentiment support...")
    with closing(sqlite3.connect(DATABASE)) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS headlines (
                id INTEGER PRIMARY KEY,
                ticker TEXT NOT NULL,
                headline TEXT NOT NULL,
                sentiment_score REAL NOT NULL, -- NEW COLUMN
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        db.commit()
    print("Database initialized.")

def add_headline(ticker: str, headline: str, sentiment: float):
    """Adds a new headline and its sentiment score to the database."""
    with closing(sqlite3.connect(DATABASE)) as db:
        db.execute(
            "INSERT INTO headlines (ticker, headline, sentiment_score) VALUES (?, ?, ?)",
            (ticker, headline, sentiment)
        )
        db.commit()

def get_headlines(ticker: str):
    """Retrieves headlines and their sentiment scores for a given ticker."""
    with closing(sqlite3.connect(DATABASE)) as db:
        cursor = db.execute(
            "SELECT headline, sentiment_score, scraped_at FROM headlines WHERE ticker = ? ORDER BY scraped_at DESC",
            (ticker,)
        )
        return [{"headline": row[0], "sentiment_score": row[1], "scraped_at": row[2]} for row in cursor.fetchall()]