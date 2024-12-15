import pandas as pd
import yfinance as yf
from datetime import datetime

def get_stock_data(ticker, start_date, end_date):
    """
    Fetch historical stock data from Yahoo Finance.
    """
    stock = yf.Ticker(ticker)
    stock_data = stock.history(start=start_date, end=end_date)
    stock_data.reset_index(inplace=True)
    return stock_data

def get_options_data(ticker):
    """
    Fetch options data for given ticker.
    """
    stock = yf.Ticker(ticker)
    expiration_dates = stock.options
    options_data = []
    for date in expiration_dates:
        try:
            opt = stock.option_chain(date)
            calls = opt.calls
            puts = opt.puts
            calls['optionType'] = 'call'
            puts['optionType'] = 'put'
            calls['expirationDate'] = date
            puts['expirationDate'] = date
            options_data.append(calls)
            options_data.append(puts)
        except Exception as e:
            print(f"Error fetching options for date {date}: {e}")
            continue
    options_df = pd.concat(options_data, ignore_index=True)
    return options_df

if __name__ == "__main__":
    ticker = 'AAPL'
    start_date = '2018-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    stock_data = get_stock_data(ticker, start_date, end_date)
    options_data = get_options_data(ticker)
    # Save data to CSV
    stock_data.to_csv(f'data/stock_data_{ticker}.csv', index=False)
    options_data.to_csv(f'data/options_data_{ticker}.csv', index=False)
