# backend/models/train_lstm_option_pricing.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import os

# Configuration
DATA_PATH = "../data/merged_data_with_features_AAPL.csv"  # Update as needed
MODEL_SAVE_PATH = "lstm_option_pricing.keras"
TIME_STEPS = 60  # Number of past time steps to consider
FEATURES = ['Close', 'strike', 'T', 'delta', 'gamma', 'theta', 'vega', 'rho', 'impliedVolatility']

def load_data():
    data = pd.read_csv(DATA_PATH)
    data = data.sort_values('Date')  # Ensure data is sorted by date
    return data

def preprocess_data(data):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data[FEATURES])
    return scaled_data, scaler

def create_sequences(data, time_steps):
    X = []
    y = []
    for i in range(time_steps, len(data)):
        X.append(data[i-time_steps:i])
        y.append(data[i][0])  # Assuming 'Close' is the target
    X, y = np.array(X), np.array(y)
    return X, y

def build_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_model():
    data = load_data()
    scaled_data, scaler = preprocess_data(data)
    X, y = create_sequences(scaled_data, TIME_STEPS)
    
    # Split into training and testing sets
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    model = build_model((X_train.shape[1], X_train.shape[2]))
    
    early_stop = EarlyStopping(monitor='val_loss', patience=10)
    
    history = model.fit(
        X_train, y_train,
        batch_size=32,
        epochs=100,
        validation_data=(X_test, y_test),
        callbacks=[early_stop]
    )
    
    # Save the model
    model.save(MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train_model()
