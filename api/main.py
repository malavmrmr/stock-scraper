from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Literal
import sys, os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.news_api_scraper import scrape_from_news_api
from scrapers.fmp_scraper import scrape_from_fmp
from scrapers.cnbctv18_scraper import scrape_cnbctv18
from scrapers.google_scraper import scrape_from_google
from database import init_db, add_headline, get_headlines
from services.sentiment import analyze_sentiment
from services.cleaner import clean_headlines

init_db()

class StockRequest(BaseModel):
    ticker: str
    source: Literal['google', 'newsapi', 'fmp', 'cnbctv18']
    from_date: date
    to_date: date

app = FastAPI(title="Stock Market Scraper API", version="0.12.0")

def process_scraping(ticker: str, source: str, from_date: str, to_date: str):
    scraper_map = {
        'google': scrape_from_google,
        'newsapi': scrape_from_news_api,
        'fmp': scrape_from_fmp,
        'cnbctv18': scrape_cnbctv18
    }
    
    print(f"--- Background task started for {ticker} from source: {source} ---")
    scraper_function = scraper_map.get(source)
    if not scraper_function:
        return
        
    articles = scraper_function(ticker, from_date, to_date)
    cleaned_articles = clean_headlines(articles, ticker)
    
    if cleaned_articles:
        print(f"--- Analyzing and saving {len(cleaned_articles)} headlines for {ticker} ---")
        for article in cleaned_articles:
            sentiment = analyze_sentiment(article['title'])
            # Pass the new 'published_at' field to the database
            add_headline(ticker, article['title'], article['url'], article.get('published_at', ''), sentiment)
    else:
        print(f"--- No results found for {ticker} from {source} after cleaning ---")

@app.post("/scrape")
def scrape_stock(request: StockRequest, background_tasks: BackgroundTasks):
    from_date_str = request.from_date.isoformat()
    to_date_str = request.to_date.isoformat()
    background_tasks.add_task(process_scraping, request.ticker, request.source, from_date_str, to_date_str)
    return {"status": "success", "message": f"Scraping from '{request.source}' for '{request.ticker}' initiated."}

@app.get("/results/{ticker}")
def read_results(ticker: str):
    results = get_headlines(ticker)
    return {"ticker": ticker, "results": results}