# backend/app/utils/finnhub_client.py
import finnhub
from app.config import settings

finnhub_client = finnhub.Client(api_key=settings.finnhub_api_key)

def get_stock_quote(ticker: str):
    try:
        quote = finnhub_client.quote(ticker)
        return quote
    except Exception:
        return None

def get_stock_profile(ticker: str):
    try:
        profile = finnhub_client.company_profile2(symbol=ticker)
        return profile
    except Exception:
        return None
