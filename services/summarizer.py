from transformers import pipeline

# Create a reusable pipeline for summarization.
# This will download a model (approx. 250MB) on the first run.
print("Loading summarization model...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
print("Summarization model loaded successfully.")

def generate_summary(text: str):
    """
    Generates a summary from a block of text.
    """
    if not text:
        return "Not enough text to generate a summary."

    # The model works best with a certain length of text.
    # We'll limit the input to the first 1024 characters.
    max_length = 1024
    truncated_text = text[:max_length]

    # Generate summary with min and max length for the output
    summary = summarizer(truncated_text, max_length=100, min_length=25, do_sample=False)

    return summary[0]['summary_text']