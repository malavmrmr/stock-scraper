import requests

# --- PASTE YOUR MARKETAUX API TOKEN HERE ---
API_TOKEN = "JLChCy3VZzaVfRHpGO4n5zCof3OSaOb65EaVWsnk"

def scrape_from_marketaux(ticker: str, from_date: str, to_date: str):
    """
    Fetches news for a ticker from the MarketAux API.
    """
    if "PASTE" in API_TOKEN:
        print("ERROR: MarketAux API token is not set.")
        return []

    # The MarketAux API endpoint for all news
    url = "https://api.marketaux.com/v1/news/all"

    params = {
        "api_token": API_TOKEN,
        "symbols": ticker,
        "language": "en",
        "limit": 50 # The free plan might have a lower limit
    }

    articles = []
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # The articles are in the 'data' key
        for article in data.get("data", []):
            articles.append({
                'title': article.get('title'),
                'url': article.get('url'),
                'published_at': article.get('published_at', '').split('T')[0]
            })
    except requests.RequestException as e:
        print(f"Error fetching from MarketAux API: {e}")
        try:
            print(f"API Error Response: {response.json()}")
        except:
            pass
        return []

    return articles