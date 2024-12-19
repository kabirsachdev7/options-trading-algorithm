# backend/app/utils/data_fetcher.py

import os
import requests
import pandas as pd
import yfinance as yf
from fastapi import HTTPException

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

def fetch_historical_data_alpha(ticker: str, period: str = "2y") -> pd.DataFrame:
    """
    Fetch historical data from Alpha Vantage.
    period is interpreted:
     '2y' ~ last 500 trading days
     '1y' ~ last 250 trading days
     'max' ~ full data
    """
    if not ALPHAVANTAGE_API_KEY:
        raise HTTPException(status_code=500, detail="Alpha Vantage API key not configured.")

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "apikey": ALPHAVANTAGE_API_KEY,
        "outputsize": "full"
    }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Alpha Vantage request failed with code {r.status_code}.")

    data = r.json()
    if "Time Series (Daily)" not in data:
        # No data found
        raise HTTPException(status_code=404, detail=f"No Alpha Vantage data for {ticker}.")

    ts = data["Time Series (Daily)"]
    df = pd.DataFrame.from_dict(ts, orient='index', dtype=float)
    df.index = pd.to_datetime(df.index)
    df.rename(columns={
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close',
        '5. adjusted close': 'Adj Close',
        '6. volume': 'Volume'
    }, inplace=True)
    df.sort_index(inplace=True)

    # Filter by period
    if period == "2y":
        df = df.last('500D')
    elif period == "1y":
        df = df.last('250D')
    # 'max' means full data already fetched

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No Alpha Vantage data for {ticker} in {period} period.")

    return df

def fetch_historical_data(ticker: str) -> pd.DataFrame:
    """
    Attempt to fetch 2y data from Alpha Vantage first.
    If no data found, fallback to Yahoo Finance.
    """
    try:
        df = fetch_historical_data_alpha(ticker, "2y")
        df['data_source'] = 'Alpha Vantage'
        return df
    except HTTPException as e:
        if e.status_code == 404:
            # Fallback to yfinance
            df_yf = yf.Ticker(ticker).history(period="2y", interval='1d')
            if df_yf.empty:
                # Try shorter period or max with yfinance
                df_yf = yf.Ticker(ticker).history(period="1y", interval='1d')
                if df_yf.empty:
                    df_yf = yf.Ticker(ticker).history(period="max", interval='1d')
                    if df_yf.empty:
                        raise HTTPException(status_code=404, detail=f"No historical data found for {ticker} via Alpha Vantage or Yahoo Finance.")
            df_yf['data_source'] = 'Yahoo Finance'
            return df_yf
        else:
            # Some other error from Alpha Vantage
            raise e

def fetch_option_chain(ticker: str):
    """
    Fetch option chain from Yahoo Finance as previously.
    """
    ticker_obj = yf.Ticker(ticker)
    expirations = ticker_obj.options
    if not expirations:
        raise HTTPException(status_code=404, detail=f"No option chain available for {ticker}.")
    expiration_str = expirations[0]
    chain = ticker_obj.option_chain(expiration_str)
    calls = chain.calls.copy()
    puts = chain.puts.copy()
    if calls.empty and puts.empty:
        raise HTTPException(status_code=404, detail=f"No option chain data for {ticker} at {expiration_str}.")
    return calls, puts, expiration_str
