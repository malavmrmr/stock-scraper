import re # Import the regular expressions library
from playwright.sync_api import sync_playwright, TimeoutError
from bs4 import BeautifulSoup

def scrape_yahoo_finance(ticker: str):
    """
    Scrapes Yahoo Finance using a robust pattern-matching method to find news links.
    """
    url = f"https://finance.yahoo.com/quote/{ticker}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until='domcontentloaded')

            try:
                page.locator('button[value="agree"]').click(timeout=5000)
                print("Successfully clicked the consent button.")
            except TimeoutError:
                print("Consent button not found or already accepted, continuing...")

            # Wait for network activity to be idle, a good sign that dynamic content has loaded.
            page.wait_for_load_state('networkidle', timeout=15000)
            print("Page network is idle. Content should be loaded.")

            html = page.content()
            browser.close()

    except Exception as e:
        print(f"Error with Playwright for {ticker}: {e}")
        return []

    # --- NEW PATTERN-BASED PARSING ---
    soup = BeautifulSoup(html, 'html.parser')
    headlines = []
    
    # Find all 'a' tags where the href contains '/news/' using a regular expression
    # This is highly resilient to changes in CSS classes, IDs, or layout.
    news_links = soup.find_all('a', href=re.compile(r'/news/'))
    
    for link in news_links:
        # We only want actual headlines, which are usually inside h3 tags
        headline_tag = link.find('h3')
        if headline_tag:
            # .get_text(strip=True) cleans up whitespace
            text = headline_tag.get_text(strip=True)
            if text and text not in headlines: # Avoid duplicates
                headlines.append(text)

    if not headlines:
        print(f"No headlines found for {ticker} using the pattern-matching method.")
        return []

    return headlines