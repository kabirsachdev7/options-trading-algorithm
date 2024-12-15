import pandas as pd
import numpy as np
from scipy.stats import norm

def calculate_implied_volatility(row, r):
    """
    Calculate implied volatility using the Black-Scholes model and Newton-Raphson method.
    """
    S = row['Close']
    K = row['strike']
    T = row['T']
    option_price = row['lastPrice']
    option_type = row['optionType']
    sigma = 0.2  # initial guess

    for i in range(100):
        d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if option_type == 'call':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            vega = S * norm.pdf(d1) * np.sqrt(T)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            vega = S * norm.pdf(d1) * np.sqrt(T)
        price_diff = option_price - price
        if abs(price_diff) < 1e-5:
            break
        sigma += price_diff / (vega + 1e-8)
    return sigma

def calculate_greeks(row, r):
    """
    Calculate Greeks using the Black-Scholes model.
    """
    S = row['Close']
    K = row['strike']
    T = row['T']
    sigma = row['impliedVolatility']
    option_type = row['optionType']
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    delta = norm.cdf(d1) if option_type == 'call' else norm.cdf(d1) - 1
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
             - r * K * np.exp(-r * T) * norm.cdf(d2 if option_type == 'call' else -d2)) / 365
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    rho = (K * T * np.exp(-r * T) * norm.cdf(d2 if option_type == 'call' else -d2)) / 100
    return pd.Series([delta, gamma, theta, vega, rho], index=['delta', 'gamma', 'theta', 'vega', 'rho'])

def add_features(merged_data):
    """
    Add implied volatility and Greeks to the dataset.
    """
    r = get_risk_free_rate()
    merged_data['impliedVolatility'] = merged_data.apply(lambda row: calculate_implied_volatility(row, r), axis=1)
    greeks = merged_data.apply(lambda row: calculate_greeks(row, r), axis=1)
    merged_data = pd.concat([merged_data, greeks], axis=1)
    return merged_data

def get_risk_free_rate():
    """
    Placeholder for risk-free rate retrieval.
    """
    return 0.01  # 1% annual risk-free rate

if __name__ == "__main__":
    ticker = 'AAPL'
    merged_data = pd.read_csv(f'data/merged_data_{ticker}.csv')
    merged_data_with_features = add_features(merged_data)
    merged_data_with_features.to_csv(f'data/merged_data_with_features_{ticker}.csv', index=False)
