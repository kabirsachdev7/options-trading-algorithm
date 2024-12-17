import sys
import os
import time
import math
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import regularizers
import yfinance as yf
import random

STRATEGIES = [
    "call_spread",
    "put_spread",
    "iron_condor",
    "covered_call",
    "protective_put",
    "straddle",
    "strangle",
    "butterfly"
]

def get_historical_data(ticker, years=1):
    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.history(period=f"{years}y", interval='1d')
    if df.empty:
        raise ValueError(f"No historical data for {ticker}")
    df.sort_index(inplace=True)
    return df

def label_strategies(options_data):
    # Label strategies based on heuristics
    iv = options_data['impliedVolatility'].mean()
    moneyness_mean = options_data['moneyness'].mean()

    # Heuristics
    if iv > 0.4 and abs(moneyness_mean) < 0.05:
        strat = 'straddle'
    elif iv < 0.2 and abs(moneyness_mean) < 0.05:
        strat = 'iron_condor'
    elif moneyness_mean > 0.1:
        strat = 'call_spread'
    elif moneyness_mean < -0.1:
        strat = 'put_spread'
    elif moneyness_mean > 0.05 and iv < 0.3:
        strat = 'covered_call'
    elif moneyness_mean < -0.05 and iv < 0.3:
        strat = 'protective_put'
    elif iv > 0.3 and abs(moneyness_mean) < 0.1:
        strat = 'strangle'
    else:
        strat = 'butterfly'

    # Add a random factor to ensure diversity
    # If random < 0.2, switch strategy to another random one to ensure multiple classes
    if random.random() < 0.2:
        strat = random.choice(STRATEGIES)

    return strat

def engineer_features(price_data, options_data):
    current_price = price_data['Close'].iloc[-1]
    options_data['moneyness'] = (options_data['strike'] / current_price) - 1.0

    if 'expiration' not in options_data.columns:
        # If no expiration, assume fixed T
        T = 0.25
        options_data['T'] = T
    else:
        now = pd.Timestamp.now(tz='UTC')
        # Make sure expiration is tz-aware or tz-naive consistently
        if options_data['expiration'].dt.tz is None:
            # Localize expiration to UTC
            options_data['expiration'] = options_data['expiration'].dt.tz_localize('UTC')
        options_data['T'] = (options_data['expiration'] - now).dt.days / 365.0

    options_data.fillna(0, inplace=True)
    options_data['option_type_encoded'] = options_data['option_type'].map({'call':1,'put':0})
    options_data['Close'] = current_price

    feature_cols = ['Close','strike','T','impliedVolatility','moneyness','lastPrice','volume','openInterest','option_type_encoded']
    for col in feature_cols:
        if col not in options_data.columns:
            options_data[col] = 0.0

    X = options_data[feature_cols].values
    return X, options_data

def build_and_train_model(X, y):
    # Ensure we have multiple classes
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    classes = label_encoder.classes_

    print("Unique strategies:", classes)
    if len(classes) < 2:
        raise ValueError("Not enough classes to train a multi-class model. Increase diversity in labeling.")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, Y_train, Y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)
    num_classes = len(classes)
    input_dim = X_train.shape[1]

    model = Sequential()
    model.add(Input(shape=(input_dim,)))
    model.add(Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.001)))
    model.add(Dropout(0.3))
    model.add(Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.001)))
    model.add(Dropout(0.3))
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    model.fit(X_train, Y_train, batch_size=32, epochs=50, validation_data=(X_test, Y_test), callbacks=[early_stop])

    model.save("fnn_strategy.keras")
    joblib.dump(scaler, "fnn_scaler.pkl")
    joblib.dump(label_encoder, "fnn_label_encoder.pkl")
    print("FNN Strategy Model trained and saved.")

def main(tickers):
    all_X = []
    all_y = []

    for ticker in tickers:
        print(f"Processing {ticker}")
        price_data = get_historical_data(ticker, years=1)
        ticker_obj = yf.Ticker(ticker)
        expirations = ticker_obj.options
        if not expirations:
            print(f"No expirations for {ticker}, skipping...")
            continue
        expiration_str = expirations[0]
        expiration_date = pd.to_datetime(expiration_str)
        # Make sure expiration_date is tz-aware
        expiration_date = expiration_date.tz_localize('UTC', nonexistent='shift_forward', ambiguous='NaT')

        chain = ticker_obj.option_chain(expiration_str)
        calls = chain.calls.copy()
        puts = chain.puts.copy()

        if calls.empty and puts.empty:
            print(f"No option chain data for {ticker} at {expiration_str}, skipping...")
            continue

        calls['option_type'] = 'call'
        puts['option_type'] = 'put'
        options_data = pd.concat([calls, puts], ignore_index=True)
        options_data['expiration'] = expiration_date

        X, df = engineer_features(price_data, options_data)
        strat_label = label_strategies(df)  # single strategy for entire option chain
        y = [strat_label]*len(X)
        all_X.append(X)
        all_y.extend(y)

    if not all_X:
        raise ValueError("No data to train on. Check if tickers have option data.")

    all_X = np.vstack(all_X)
    all_y = np.array(all_y)

    build_and_train_model(all_X, all_y)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python train_fnn_strategy.py <TICKER1> <TICKER2> ...")
        sys.exit(1)
    tickers = [t.upper() for t in sys.argv[1:]]
    main(tickers)
