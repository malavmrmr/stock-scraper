from transformers import pipeline

# Create a single, reusable pipeline for sentiment analysis.
# The first time this runs, it will download the FinBERT model (approx. 400MB).
print("Loading FinBERT sentiment analysis model...")
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
print("FinBERT model loaded successfully.")

def analyze_sentiment(text: str):
    """
    Analyzes the sentiment of a text using the FinBERT model.
    Returns a score between -1 (negative) and 1 (positive).
    """
    # Truncate text to the model's max input size to avoid errors
    truncated_text = text[:512]

    results = sentiment_pipeline(truncated_text)

    # The model returns a label ('positive', 'negative', 'neutral') and a score.
    # We'll convert the label and score into a single compound score.
    score = results[0]['score']
    label = results[0]['label']

    if label == 'negative':
        return -score
    elif label == 'positive':
        return score
    else: # neutral
        return 0.0