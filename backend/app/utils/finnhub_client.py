# backend/app/utils/finnhub_client.py

import finnhub
import os
from app.config import settings

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=settings.finnhub_api_key)

def get_stock_quote(ticker: str):
    """
    Fetches the latest stock quote for the given ticker.
    """
    try:
        quote = finnhub_client.quote(ticker)
        return quote  # Returns a dictionary with current price, etc.
    except Exception as e:
        print(f"Error fetching quote for {ticker}: {e}")
        return None

def get_stock_profile(ticker: str):
    """
    Fetches the stock profile for the given ticker.
    """
    try:
        profile = finnhub_client.company_profile2(symbol=ticker)
        return profile  # Returns a dictionary with company details
    except Exception as e:
        print(f"Error fetching profile for {ticker}: {e}")
        return None

# Add more utility functions as needed
