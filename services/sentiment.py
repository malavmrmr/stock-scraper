from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Create a single, reusable analyzer instance
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str):
    """
    Analyzes the sentiment of a text and returns the compound score.
    - Positive sentiment: compound score >= 0.05
    - Neutral sentiment: -0.05 < compound score < 0.05
    - Negative sentiment: compound score <= -0.05
    """
    # The polarity_scores() method returns a dictionary.
    # We are most interested in the 'compound' score.
    score = analyzer.polarity_scores(text)
    return score['compound']