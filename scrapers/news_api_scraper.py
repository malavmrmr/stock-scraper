import requests
from urllib.parse import quote_plus

# --- IMPORTANT: PASTE YOUR API KEYS HERE ---
NEWS_API_KEY = "be1f8510b6214925a12c16e409d10bb4"
FMP_API_KEY = "LHBwcmj9y4zNmfUUNRQpy0bYqVSX0xcd"

def get_company_name(ticker: str):
    """Fetches the full company name from a ticker using the FMP API."""
    if "PASTE" in FMP_API_KEY:
        return ""
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data and 'companyName' in data[0]:
            return data[0]['companyName'].replace(" Inc.", "").replace(" Ltd.", "")
    except requests.RequestException:
        return ""
    return ""

def scrape_from_news_api(ticker: str, from_date: str, to_date: str):
    """Fetches news from NewsAPI.org within a specific date range."""
    if "PASTE" in NEWS_API_KEY:
        print("ERROR: NewsAPI.org API key is not set.")
        return []

    company_name = get_company_name(ticker)
    search_query = f'"{ticker}" OR "{company_name}"' if company_name else ticker
    encoded_query = quote_plus(search_query)
    print(f"NewsAPI encoded query: {encoded_query}")
    
    url = (f"https://newsapi.org/v2/everything?"
           f"q={encoded_query}"
           f"&from={from_date}"
           f"&to={to_date}"
           f"&language=en"
           f"&sortBy=relevancy"
           f"&apiKey={NEWS_API_KEY}")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    articles = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        for article in data.get("articles", []):
            articles.append({
                'title': article.get('title'),
                'url': article.get('url'),
                'published_at': article.get('publishedAt', '').split('T')[0] # Get just the date part
            })
    except requests.RequestException as e:
        print(f"Error fetching from NewsAPI: {e}")
        return []
    
    return articles