import streamlit as st
import sys
import os
import time
from datetime import date, timedelta
import pandas as pd
import plotly.express as px

# Add the project root to the Python path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Direct Imports (No FastAPI needed) ---
from scrapers.news_api_scraper import scrape_from_news_api
from scrapers.fmp_scraper import scrape_from_fmp, get_indian_stocks
from scrapers.cnbctv18_scraper import scrape_cnbctv18
from scrapers.google_scraper import scrape_from_google
from scrapers.finnhub_scraper import scrape_from_finnhub
from database import init_db, add_headline, get_headlines, get_sentiment_over_time
from services.sentiment import analyze_sentiment
from services.cleaner import clean_headlines
from services.summarizer import generate_summary

# --- Initialize the database on startup ---
init_db()

# --- Page Configuration ---
st.set_page_config(page_title="Market Pulse Analyzer", page_icon="📈", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.header("🇮🇳 Popular Indian Stocks")
    stock_list = get_indian_stocks()
    if stock_list:
        for stock in stock_list:
            if st.button(f"{stock['symbol']} - {stock['name']}", use_container_width=True):
                st.session_state.ticker = stock['symbol']
    else:
        st.warning("Could not fetch stock list.")

# --- Main App UI ---
st.title("📈 Market Pulse News Analyzer")
st.markdown("This application fetches news, analyzes sentiment, and provides an AI-generated summary.")

if 'ticker' not in st.session_state:
    st.session_state.ticker = 'RELIANCE'
ticker_input = st.text_input("Enter a stock ticker (or select from sidebar):", st.session_state.ticker).upper()

col2, col3, col4 = st.columns([1, 1, 1])
with col2:
    source = st.selectbox("Select news source:", ("newsapi", "google", "marketaux", "finnhub", "fmp", "cnbctv18"))
with col3:
    from_date = st.date_input("Start Date", date.today() - timedelta(days=30))
with col4:
    to_date = st.date_input("End Date", date.today())

# --- Form and Scraping Logic ---
with st.form("scrape_form"):
    ticker_to_scrape = ticker_input
    submitted = st.form_submit_button("Fetch & Analyze News")
    if submitted:
        if from_date > to_date:
            st.error("Error: Start Date cannot be after End Date.")
        else:
            with st.spinner(f"Processing request for {ticker_to_scrape}... This might take a minute."):
                # --- Direct Call to Scraping Logic (No API) ---
                scraper_map = {
                    'google': scrape_from_google, 'newsapi': scrape_from_news_api,
                    'fmp': scrape_from_fmp, 'cnbctv18': scrape_cnbctv18,
                     'finnhub': scrape_from_finnhub
                }
                scraper_function = scraper_map.get(source)
                if scraper_function:
                    from_date_str = from_date.isoformat()
                    to_date_str = to_date.isoformat()
                    articles = scraper_function(ticker_to_scrape, from_date_str, to_date_str)
                    cleaned_articles = clean_headlines(articles, ticker_to_scrape)
                    
                    if cleaned_articles:
                        st.write(f"Found {len(cleaned_articles)} relevant articles. Analyzing and saving...")
                        for article in cleaned_articles:
                            sentiment = analyze_sentiment(article['title'])
                            add_headline(ticker_to_scrape, article['title'], article['url'], article.get('published_at', ''), sentiment)
                        st.success("Processing Complete!")
                    else:
                        st.warning("No new articles found for the selected criteria.")
                else:
                    st.error("Invalid source selected.")

# --- Display Results Section ---
st.header(f"Analysis for {ticker_to_scrape}")

# --- Get data directly from the database ---
results_data = get_headlines(ticker_to_scrape)
sentiment_data = get_sentiment_over_time(ticker_to_scrape)

if not results_data:
    st.info("No results found in the database for this ticker yet. Click 'Fetch & Analyze' to begin.")
else:
    # --- Executive Summary ---
    st.subheader("Executive Summary")
    with st.spinner("Generating AI summary..."):
        all_headlines_text = ". ".join([item['headline'] for item in results_data])
        summary = generate_summary(all_headlines_text)
        st.info(summary)

    # --- Analytics Dashboard ---
    st.subheader("Analytics Dashboard")
    if sentiment_data:
        df_sentiment = pd.DataFrame(sentiment_data)
        df_sentiment['day'] = pd.to_datetime(df_sentiment['day'])
        fig = px.line(df_sentiment, x='day', y='avg_sentiment', title='Sentiment Trend Over Time', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to display analytics.")

    # --- Results Table ---
    st.subheader("Latest News Articles")
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

# --- Footer ---
st.markdown("---")
st.markdown("Developed by Malav | Follow on X: [@YourXHandle](https://x.com/YourXHandle)")
st.markdown("Powered by Streamlit | Data sourced from various APIs.")