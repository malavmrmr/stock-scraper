from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI(
    title="Stock Market Scraper API",
    description="An API to fetch and analyze stock market news.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the Stock Scraper API!"}

@app.get("/status")
def get_status():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "API is running"}