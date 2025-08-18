from playwright.sync_api import sync_playwright

# This script is ONLY for debugging to find new selectors.
def debug_yahoo_selectors():
    ticker = "AAPL"
    url = f"https://finance.yahoo.com/quote/{ticker}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        # This command pauses the script and opens the Inspector tool.
        print("\n>>> SCRIPT PAUSED <<<")
        print(">>> Use the Playwright Inspector to find new selectors.")
        print(">>> Close the browser window to resume and end the script.")
        page.pause()

if __name__ == "__main__":
    debug_yahoo_selectors()