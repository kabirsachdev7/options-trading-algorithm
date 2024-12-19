# backend/app/utils/news_fetcher.py

import os
import requests
from fastapi import HTTPException

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def fetch_top_business_news():
    if not NEWSAPI_KEY:
        raise HTTPException(status_code=500, detail="NEWSAPI_KEY not set.")
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": "business",
        "language": "en",
        "apiKey": NEWSAPI_KEY,
        "pageSize": 5  # top 5 headlines
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch news from NewsAPI.")
    data = r.json()
    if data.get("status") != "ok":
        raise HTTPException(status_code=500, detail="Error from NewsAPI: " + data.get("message", "unknown error"))
    articles = data.get("articles", [])
    # Return a simplified list of dicts
    headlines = []
    for art in articles:
        headlines.append({
            "title": art.get("title"),
            "description": art.get("description"),
            "url": art.get("url"),
            "source": art["source"].get("name") if art.get("source") else "Unknown"
        })
    return headlines
