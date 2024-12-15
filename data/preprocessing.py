import pandas as pd
import numpy as np

def preprocess_data(stock_data, options_data):
    """
    Preprocess and merge stock and options data using an asof merge to align dates.
    """
    # Convert date columns to datetime with UTC timezone
    stock_data['Date'] = pd.to_datetime(stock_data['Date'], utc=True)
    options_data['lastTradeDate'] = pd.to_datetime(options_data['lastTradeDate'], utc=True)
    options_data['expirationDate'] = pd.to_datetime(options_data['expirationDate'], utc=True)

    # Sort both DataFrames by date to prepare for merge_asof
    stock_data.sort_values('Date', inplace=True)
    options_data.sort_values('lastTradeDate', inplace=True)

    # Perform an asof merge: for each lastTradeDate, find the nearest Date in stock_data that is <= lastTradeDate
    merged_data = pd.merge_asof(
        options_data,
        stock_data,
        left_on='lastTradeDate',
        right_on='Date',
        direction='backward',
        allow_exact_matches=True
    )

    # After merging, drop rows where the merge didn't find a corresponding stock Date
    merged_data.dropna(subset=['Close'], inplace=True)

    # Calculate time to maturity in years
    merged_data['T'] = (merged_data['expirationDate'] - merged_data['lastTradeDate']).dt.days / 365.0

    # Filter out options with negative or zero time to maturity
    merged_data = merged_data[merged_data['T'] > 0]

    # Calculate moneyness
    merged_data['moneyness'] = merged_data['Close'] / merged_data['strike']

    # Handle missing values by forward filling
    merged_data.ffill(inplace=True)

    return merged_data

def get_risk_free_rate():
    """
    Placeholder for risk-free rate retrieval.
    """
    return 0.01  # 1% annual risk-free rate

if __name__ == "__main__":
    ticker = 'AAPL'
    # Load the stock data
    stock_data = pd.read_csv(f'data/stock_data_{ticker}.csv')
    # Load the options data
    options_data = pd.read_csv(f'data/options_data_{ticker}.csv')

    print("Stock Data Date Range:", stock_data['Date'].min(), "to", stock_data['Date'].max())
    print("First few rows of Stock Data:")
    print(stock_data.head())

    print("Options Data lastTradeDate Range:", options_data['lastTradeDate'].min(), "to", options_data['lastTradeDate'].max())
    print("First few rows of Options Data:")
    print(options_data.head())

    # Preprocess and merge the data
    merged_data = preprocess_data(stock_data, options_data)
    print("Merged Data Shape:", merged_data.shape)
    print("First few rows of Merged Data:")
    print(merged_data.head())

    # Save the merged data
    merged_data.to_csv(f'data/merged_data_{ticker}.csv', index=False)
    print(f"Saved merged data to 'data/merged_data_{ticker}.csv'")
