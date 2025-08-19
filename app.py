import streamlit as st
import uvicorn
import sys
import os
import threading
import time
from datetime import date, timedelta
import pandas as pd
import requests
import plotly.express as px

# Add the project root to the Python path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ---
# This section is your existing api/main.py, but now it's a function
# ---
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Literal

from scrapers.news_api_scraper import scrape_from_news_api
from scrapers.fmp_scraper import scrape_from_fmp, get_indian_stocks
from scrapers.cnbctv18_scraper import scrape_cnbctv18
from scrapers.google_scraper import scrape_from_google
from database import init_db, add_headline, get_headlines, get_sentiment_over_time
from services.sentiment import analyze_sentiment
from services.cleaner import clean_headlines

def run_fastapi_app():
    init_db()

    class StockRequest(BaseModel):
        ticker: str
        source: Literal['google', 'newsapi', 'fmp', 'cnbctv18']
        from_date: date
        to_date: date

    app = FastAPI(title="Stock Market Scraper API")

    def process_scraping(ticker: str, source: str, from_date: str, to_date: str):
        scraper_map = { 'google': scrape_from_google, 'newsapi': scrape_from_news_api, 'fmp': scrape_from_fmp, 'cnbctv18': scrape_cnbctv18 }
        scraper_function = scraper_map.get(source)
        if not scraper_function: return
        articles = scraper_function(ticker, from_date, to_date)
        cleaned_articles = clean_headlines(articles, ticker)
        if cleaned_articles:
            for article in cleaned_articles:
                sentiment = analyze_sentiment(article['title'])
                add_headline(ticker, article['title'], article['url'], article.get('published_at', ''), sentiment)

    @app.post("/scrape")
    def scrape_stock(request: StockRequest, background_tasks: BackgroundTasks):
        from_date_str = request.from_date.isoformat()
        to_date_str = request.to_date.isoformat()
        background_tasks.add_task(process_scraping, request.ticker, request.source, from_date_str, to_date_str)
        return {"status": "success", "message": f"Scraping initiated."}

    @app.get("/results/{ticker}")
    def read_results(ticker: str):
        return {"ticker": ticker, "results": get_headlines(ticker)}
    
    @app.get("/analytics/{ticker}")
    def read_analytics(ticker: str):
        return {"ticker": ticker, "sentiment_trend": get_sentiment_over_time(ticker)}
        
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ---
# This section is your existing frontend.py
# ---
st.set_page_config(page_title="Stock Market Scraper", page_icon="📈", layout="wide")
API_URL = "http://127.0.0.1:8000"

daemon = threading.Thread(name='FastAPI Backend', target=run_fastapi_app, daemon=True)
daemon.start()
time.sleep(5)

# --- NEW: HEADER SECTION ---
st.title("📈 Stock Market News Scraper & Analyzer for Vishal and Maulik")
st.markdown("This application fetches the latest news for a selected stock, analyzes the sentiment of each headline, and displays the results in a table and chart.")

with st.sidebar:
    st.header("🇮🇳 Popular Indian Stocks")
    stock_list = get_indian_stocks()
    if stock_list:
        for stock in stock_list:
            if st.button(f"{stock['symbol']} - {stock['name']}", use_container_width=True):
                st.session_state.ticker = stock['symbol']
    else:
        st.warning("Could not fetch stock list.")

if 'ticker' not in st.session_state: st.session_state.ticker = 'RELIANCE'
ticker_input = st.text_input("Enter a stock ticker (or select from sidebar):", st.session_state.ticker).upper()
col2, col3, col4 = st.columns([1, 1, 1])
with col2: source = st.selectbox("Select news source:", ("newsapi", "google", "fmp", "cnbctv18"))
with col3: from_date = st.date_input("Start Date", date.today() - timedelta(days=30))
with col4: to_date = st.date_input("End Date", date.today())
with st.form("scrape_form"):
    ticker_to_scrape = ticker_input
    submitted = st.form_submit_button("Fetch & Analyze News")
    if submitted:
        if from_date > to_date: st.error("Error: Start Date cannot be after End Date.")
        else:
            with st.status(f"Processing request for {ticker_to_scrape}...", expanded=True) as status:
                try:
                    st.write(f"Sending scraping request to the backend for source: '{source}'...")
                    payload = {"ticker": ticker_to_scrape, "source": source, "from_date": from_date.isoformat(), "to_date": to_date.isoformat()}
                    requests.post(f"{API_URL}/scrape", json=payload)
                    st.write("Backend job started successfully. Waiting for results...")
                    for i in range(6):
                        time.sleep(5)
                        st.write(f"Checking for results (attempt {i+1}/6)...")
                        results_response = requests.get(f"{API_URL}/results/{ticker_to_scrape}")
                        if results_response.status_code == 200 and results_response.json().get("results"):
                            st.write("Results found!")
                            status.update(label="Processing Complete!", state="complete")
                            break
                    else:
                        st.warning("Job is taking longer than usual.")
                        status.update(label="Job is running...", state="running")
                except requests.ConnectionError:
                    st.error("Connection Error: Could not connect to the backend API.")
                    status.update(label="Connection Error!", state="error")

st.header(f"Analytics Dashboard for {ticker_to_scrape}")
try:
    analytics_response = requests.get(f"{API_URL}/analytics/{ticker_to_scrape}")
    if analytics_response.status_code == 200:
        sentiment_data = analytics_response.json().get("sentiment_trend", [])
        if sentiment_data:
            df_sentiment = pd.DataFrame(sentiment_data)
            df_sentiment['day'] = pd.to_datetime(df_sentiment['day'])
            fig = px.line(df_sentiment, x='day', y='avg_sentiment', title='Sentiment Trend Over Time', markers=True)
            fig.update_yaxes(title_text='Average Sentiment Score')
            fig.update_xaxes(title_text='Date')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to display analytics. Scrape more news over several days.")
except requests.ConnectionError:
    st.error("Could not connect to the backend API for analytics.")

st.header(f"Latest Analysis Results for {ticker_to_scrape}")
try:
    results_response = requests.get(f"{API_URL}/results/{ticker_to_scrape}")
    results_data = results_response.json().get("results", [])
    if results_data:
        df = pd.DataFrame(results_data)
        def classify_sentiment(score):
            if score > 0.1: return "Good News"
            elif score < -0.1: return "Bad News"
            else: return "Neutral"
        df['Sentiment'] = df['sentiment_score'].apply(classify_sentiment)
        def make_clickable(url): return f'<a href="{url}" target="_blank">Read Article</a>'
        df['source_url'] = df['source_url'].apply(make_clickable)
        def color_sentiment_label(sentiment):
            if sentiment == "Good News": return 'background-color: #ccffcc; color: black'
            elif sentiment == "Bad News": return 'background-color: #ffdddd; color: black'
            else: return 'background-color: #eeeeee; color: black'
        df_display = df[['headline', 'Sentiment', 'published_at', 'source_url']]
        df_display = df_display.rename(columns={"published_at": "Published Date", "source_url": "Article Link"})
        styled_df = df_display.style.apply(lambda col: col.map(color_sentiment_label), subset=['Sentiment'])
        st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.info("No results found in the database for this ticker yet.")
except requests.ConnectionError:
    st.error("Could not connect to the backend API during results display.")

# --- NEW: FOOTER SECTION ---
st.markdown("---")
st.markdown("Developed by Malav Raval")
st.markdown("Data sourced from NewsAPI.org, FinancialModelingPrep, and others.")
