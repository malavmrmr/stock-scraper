import requests
from bs4 import BeautifulSoup

def scrape_cnbctv18(ticker: str, from_date: str, to_date: str):
    """
    Scrapes a specific stock's news page on cnbctv18.com using the direct URL pattern.
    """
    # --- THIS IS THE FINAL, CORRECT URL PATTERN ---
    # It navigates directly to the stock's page, then adds '/news'
    url = f"https://www.cnbctv18.com/market/stocks/{ticker.lower()}/news/"

    print(f"Fetching news from cnbctv18 URL: {url}")
    articles = []

    try:
        # Add headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Updated selector for the news list on the stock-specific page
        news_items = soup.select('ul.listview-lead-stories li')

        if not news_items:
            print(f"No headlines found for {ticker} on cnbctv18. The page may not exist or the structure has changed.")
            return []

        for item in news_items:
            headline_tag = item.select_one('h2 a')
            if headline_tag and headline_tag.has_attr('href'):
                title = headline_tag.get_text(strip=True)
                # The href is absolute on this page
                link = headline_tag['href']

                date_tag = item.select_one('p.list-time')
                published_at = date_tag.get_text(strip=True) if date_tag else ""

                if title and link:
                    articles.append({'title': title, 'url': link, 'published_at': published_at})

    except requests.RequestException as e:
        print(f"Error fetching from cnbctv18: {e}")
        return []

    return articles