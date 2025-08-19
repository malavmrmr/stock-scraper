import streamlit as st
import requests
import pandas as pd
import time
from datetime import date, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scrapers.fmp_scraper import get_indian_stocks

st.set_page_config(page_title="Stock Market Scraper by Malav", page_icon="📈", layout="wide")
API_URL = "http://127.0.0.1:8000"

if 'ticker' not in st.session_state:
    st.session_state.ticker = 'RELIANCE'

with st.sidebar:
    st.header("🇮🇳 Popular Indian Stocks")
    stock_list = get_indian_stocks()
    if stock_list:
        for stock in stock_list:
            if st.button(f"{stock['symbol']} - {stock['name']}", use_container_width=True):
                st.session_state.ticker = stock['symbol']
    else:
        st.warning("Could not fetch stock list. Check FMP API key.")

st.title("📈 Stock Market News Scraper & Analyzer For Vishal and Maulik")

ticker_input = st.text_input("Enter a stock ticker (or select from sidebar):", st.session_state.ticker).upper()

col2, col3, col4 = st.columns([1, 1, 1])
with col2:
    source = st.selectbox("Select news source:", ("newsapi", "google", "fmp", "cnbctv18"))
with col3:
    from_date = st.date_input("Start Date", date.today() - timedelta(days=30))
    to_date = st.date_input("End Date", date.today())

with st.form("scrape_form"):
    ticker_to_scrape = ticker_input
    submitted = st.form_submit_button("Fetch & Analyze News")
    if submitted:
        if from_date > to_date:
            st.error("Error: Start Date cannot be after End Date.")
        else:
            with st.status(f"Processing request for {ticker_to_scrape}...", expanded=True) as status:
                try:
                    st.write(f"Sending scraping request to the backend for source: '{source}'...")
                    payload = {"ticker": ticker_to_scrape, "source": source, "from_date": from_date.isoformat(), "to_date": to_date.isoformat()}
                    response = requests.post(f"{API_URL}/scrape", json=payload)
                    
                    if response.status_code != 200:
                        st.error("Failed to start the backend job. Please check the server.")
                        status.update(label="Error!", state="error")
                    else:
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
                            st.warning("Job is taking longer than usual. Please check back in a moment.")
                            status.update(label="Job is running...", state="running")
                except requests.ConnectionError:
                    st.error("Connection Error: Could not connect to the backend API. Is it running?")
                    status.update(label="Connection Error!", state="error")

st.subheader(f"Latest Analysis Results for {ticker_to_scrape}")
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
        
        def make_clickable(url):
            return f'<a href="{url}" target="_blank">Read Article</a>'
        df['source_url'] = df['source_url'].apply(make_clickable)
        
        def color_sentiment_label(sentiment):
            if sentiment == "Good News": return 'background-color: #ccffcc; color: black'
            elif sentiment == "Bad News": return 'background-color: #ffdddd; color: black'
            else: return 'background-color: #eeeeee; color: black'
            
        # --- REORDER COLUMNS TO ADD PUBLISHED DATE ---
        df_display = df[['headline', 'Sentiment', 'published_at', 'source_url']]
        df_display = df_display.rename(columns={"published_at": "Published Date", "source_url": "Article Link"})
        
        styled_df = df_display.style.apply(lambda col: col.map(color_sentiment_label), subset=['Sentiment'])
        
        st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.info("No results found in the database for this ticker yet.")
except requests.ConnectionError:
    st.error("Connection Error: Could not connect to the backend API. Is it running?")