import requests
import os

# --- IMPORTANT: PASTE YOUR SERPER API KEY HERE ---
API_KEY = "d3fb7dabccf817c08d2104ca245d1939bba01005"

def scrape_from_google(ticker: str, from_date: str, to_date: str):
    """
    Fetches news for a ticker using the Serper Google News API.
    Note: Date filtering is not supported by this API; it gets the latest news.
    """
    if "PASTE" in API_KEY:
        print("ERROR: Serper API key is not set in scrapers/google_scraper.py")
        return []

    url = "https://google.serper.dev/news"

    payload = {
        "q": f"{ticker} stock news"
    }
    headers = {
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }

    articles = []
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract title and link from the 'news' list
        for item in data.get("news", []):
            if 'title' in item and 'link' in item:
                articles.append({'title': item['title'], 'url': item['link']})

    except requests.RequestException as e:
        print(f"Error fetching from Serper API: {e}")
        return []

    return articles