import requests

API_KEY = "LHBwcmj9y4zNmfUUNRQpy0bYqVSX0xcd"

def scrape_from_fmp(ticker: str, from_date: str, to_date: str):
    """Fetches general financial news from FMP API."""
    if "PASTE" in API_KEY:
        print("ERROR: FMP API key is not set.")
        return []
    url = (f"https://financialmodelingprep.com/api/v3/news?limit=50&apikey={API_KEY}")
    print(f"Fetching general market news from FMP (date filters are not supported on this free endpoint).")
    
    articles = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            for article in data:
                if 'title' in article and 'url' in article:
                    articles.append({
                        'title': article.get('title'),
                        'url': article.get('url'),
                        'published_at': article.get('publishedDate', '').split(' ')[0] # Get just the date part
                    })
    except requests.RequestException as e:
        print(f"Error fetching from FMP API: {e}")
        return []
    
    return articles

def get_indian_stocks():
    """Gets a list of popular Indian stocks using the FMP stock screener."""
    if "PASTE" in API_KEY:
        print("ERROR: FMP API key is not set.")
        return []
    url = (f"https://financialmodelingprep.com/api/v3/stock-screener?marketCapMoreThan=10000000000&country=IN&limit=50&apikey={API_KEY}")
    stocks = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            for stock in data:
                if 'symbol' in stock and 'companyName' in stock:
                    stocks.append({'symbol': stock['symbol'], 'name': stock['companyName']})
    except requests.RequestException as e:
        print(f"Error fetching Indian stock list from FMP: {e}")
        return []
    
    return stocks