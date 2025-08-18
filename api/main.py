from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from scrapers.yahoo_finance import scrape_yahoo_finance
from database import init_db, add_headline, get_headlines
from services.sentiment import analyze_sentiment

# --- Database Initialization ---
init_db()

class StockRequest(BaseModel):
    ticker: str

app = FastAPI(
    title="Stock Market Scraper API",
    version="0.3.0" # Version up!
)

def process_scraping(ticker: str):
    """
    Background task to scrape, analyze sentiment, and save results.
    """
    print(f"--- Background task started for {ticker} ---")
    headlines = scrape_yahoo_finance(ticker)
    if headlines:
        print(f"--- Analyzing and saving {len(headlines)} headlines for {ticker} ---")
        for headline in headlines:
            # 1. Analyze sentiment
            sentiment = analyze_sentiment(headline)
            # 2. Save headline and score to DB
            add_headline(ticker, headline, sentiment)
    else:
        print(f"--- No results found for {ticker} ---")


@app.post("/scrape")
def scrape_stock(request: StockRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_scraping, request.ticker)
    return {"status": "success", "message": f"Scraping and analysis for '{request.ticker}' initiated."}


@app.get("/results/{ticker}")
def read_results(ticker: str):
    print(f"Fetching results for ticker: {ticker}")
    results = get_headlines(ticker)
    return {"ticker": ticker, "results": results}