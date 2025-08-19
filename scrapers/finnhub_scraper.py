import requests
from datetime import datetime

# --- PASTE YOUR FINNHUB API KEY HERE ---
API_KEY = "d2i6hspr01qucbnndnsgd2i6hspr01qucbnndnt0"

def scrape_from_finnhub(ticker: str, from_date: str, to_date: str):
    """
    Fetches company news for a ticker from the Finnhub API.
    """
    if "PASTE" in API_KEY:
        print("ERROR: Finnhub API key is not set.")
        return []

    # The Finnhub API endpoint for company news
    url = "https://finnhub.io/api/v1/company-news"

    params = {
        "symbol": ticker,
        "from": from_date,
        "to": to_date,
        "token": API_KEY
    }

    articles = []
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # The response is a list of articles
        for article in data:
            # Convert timestamp to a readable date
            published_date = datetime.fromtimestamp(article.get('datetime')).strftime('%Y-%m-%d')

            articles.append({
                'title': article.get('headline'),
                'url': article.get('url'),
                'published_at': published_date
            })
    except requests.RequestException as e:
        print(f"Error fetching from Finnhub API: {e}")
        return []

    return articles