# Import the function from our scraper file
from scrapers.yahoo_finance import scrape_yahoo_finance

if __name__ == "__main__":
    # Define a stock ticker to test
    target_ticker = "AAPL"  # Apple Inc.
    print(f"--- Scraping news for {target_ticker} ---")
    
    # Call the scraper function
    news_headlines = scrape_yahoo_finance(target_ticker)
    
    # Print the results
    if news_headlines:
        for i, headline in enumerate(news_headlines, 1):
            print(f"{i}: {headline}")
    else:
        print(f"Could not retrieve headlines for {target_ticker}.")