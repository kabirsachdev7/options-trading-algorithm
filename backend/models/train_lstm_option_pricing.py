import pandas as pd
import numpy as np
import yfinance as yf
import sys
import os
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def load_data(ticker):
    ticker_obj = yf.Ticker(ticker)
    data = ticker_obj.history(period="2y", interval='1d')
    if data.empty:
        raise ValueError(f"No data found for ticker {ticker}")
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    data['RSI'] = compute_rsi(data['Close'])
    data.dropna(inplace=True)
    return data

def train_model(ticker):
    data = load_data(ticker)
    features = data[['Close','SMA_50','SMA_200','RSI']]
    target = data['Close'].shift(-1)
    features = features[:-1]
    target = target[:-1]

    split = int(0.8 * len(features))
    X_train, X_test = features[:split], features[split:]
    y_train, y_test = target[:split], target[split:]

    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # LSTM expects [samples, timesteps, features], we have 1 timestep here
    X_train_scaled = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
    X_test_scaled = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))

    model = Sequential()
    model.add(LSTM(50, input_shape=(1, X_train.shape[1])))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    model.fit(X_train_scaled, y_train, epochs=20, batch_size=32, validation_data=(X_test_scaled, y_test))

    models_dir = 'models'
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    model.save(f'{models_dir}/lstm_option_pricing_{ticker}.h5')
    print(f"LSTM Option Pricing Model trained and saved for ticker {ticker}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python train_lstm_option_pricing.py <TICKER>")
        sys.exit(1)
    ticker = sys.argv[1].upper()
    train_model(ticker)
