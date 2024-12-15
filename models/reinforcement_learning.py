import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
import tensorflow as tf
import os

def build_lstm_model(input_shape):
    """
    Build and compile the LSTM model using the Functional API.
    """
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(LSTM(50, return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

if __name__ == "__main__":
    ticker = 'AAPL'
    file_path = f'data/merged_data_with_features_{ticker}.csv'

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist. Please run feature_engineering.py first.")
        exit(1)

    # Load the data
    data = pd.read_csv(file_path)

    # Verify the presence of Greek columns
    greek_columns = ['delta', 'gamma', 'theta', 'vega', 'rho']
    missing_greeks = [col for col in greek_columns if col not in data.columns]
    if missing_greeks:
        print(f"Missing Greek columns in data: {missing_greeks}")
        exit(1)
    
    print("Data shape:", data.shape)
    print("Data columns:", data.columns.tolist())
    print("Features:", ['Close', 'strike', 'T', 'delta', 'gamma', 'theta', 'vega', 'rho', 'impliedVolatility'])
    
    features = ['Close', 'strike', 'T', 'delta', 'gamma', 'theta', 'vega', 'rho', 'impliedVolatility']
    
    # Check if Data[features] is not empty
    if data[features].empty:
        print("Data[features] is empty. Please check the feature engineering process.")
        exit(1)
    
    print("Data[features] shape:", data[features].shape)
    print("First few rows of data[features]:\n", data[features].head())
    
    # Initialize MinMaxScaler
    scaler = MinMaxScaler()

    # Scale the features
    data_scaled = scaler.fit_transform(data[features])
    
    # Prepare the dataset for LSTM
    X = []
    y = []
    time_steps = 10  # Number of previous time steps to consider

    for i in range(time_steps, len(data_scaled)):
        X.append(data_scaled[i-time_steps:i])
        y.append(data_scaled[i, 0])  # Predicting 'Close' price

    X, y = np.array(X), np.array(y)

    # Reshape X for LSTM input (samples, time_steps, features)
    X = np.reshape(X, (X.shape[0], X.shape[1], X.shape[2]))

    # Split into training and testing sets
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Build the LSTM model
    model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

    # Save the model in the recommended Keras format
    model.save('models/lstm_option_pricing.keras')
    print("LSTM model trained and saved successfully.")
