import re

# List of keywords that often indicate irrelevant or spammy articles
IRRELEVANT_KEYWORDS = [
    'market report', 'zodiac sign', 'horoscope', 'recipe', 'review',
    'how to', 'guide', 'top 10', 'best deals', 'sale', 'discount',
    'astrology', 'numerology', 'sports', 'cricket', 'football', 'fashion'
]

def clean_headlines(articles: list, ticker: str):
    """
    Filters out irrelevant headlines from a list of articles.
    """
    cleaned_articles = []

    # Create a regex pattern to find any of the irrelevant keywords (case-insensitive)
    irrelevant_pattern = re.compile('|'.join(IRRELEVANT_KEYWORDS), re.IGNORECASE)

    for article in articles:
        # Check if 'title' key exists and is not None
        headline = article.get('title')
        if not headline:
            continue

        # Rule 1: Skip if the headline is too short
        if len(headline.split()) < 4:
            continue

        # Rule 2: Skip if the headline contains any irrelevant keywords
        if irrelevant_pattern.search(headline):
            continue

        cleaned_articles.append(article)

    print(f"Cleaning complete. Kept {len(cleaned_articles)} of {len(articles)} articles.")
    return cleaned_articles