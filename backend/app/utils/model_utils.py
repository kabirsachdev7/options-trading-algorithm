import os
import joblib
import numpy as np
import pandas as pd
import yfinance as yf
from tensorflow.keras.models import load_model

class ModelUtils:
    def __init__(self):
        base_path = "/app/models"
        fnn_path = os.path.join(base_path, "fnn_strategy.keras")
        fnn_scaler_path = os.path.join(base_path, "fnn_scaler.pkl")
        fnn_label_encoder_path = os.path.join(base_path, "fnn_label_encoder.pkl")

        self.fnn_model = load_model(fnn_path) if os.path.exists(fnn_path) else None
        self.fnn_scaler = joblib.load(fnn_scaler_path) if os.path.exists(fnn_scaler_path) else None
        self.fnn_label_encoder = joblib.load(fnn_label_encoder_path) if os.path.exists(fnn_label_encoder_path) else None

    def load_lstm_model(self, ticker):
        path = f"/app/models/lstm_option_pricing_{ticker}.h5"
        if os.path.exists(path):
            return load_model(path)
        raise ValueError(f"LSTM model not found for ticker {ticker}")

    def predict_option_price(self, ticker, input_data):
        # input_data is (1, time_steps, feature_count)
        lstm_model = self.load_lstm_model(ticker)
        prediction = lstm_model.predict(input_data)
        return prediction[0][0]

    def recommend_strategy(self, input_data):
        if self.fnn_model is None or self.fnn_scaler is None or self.fnn_label_encoder is None:
            return "hold"
        scaled_data = self.fnn_scaler.transform(input_data)
        preds = self.fnn_model.predict(scaled_data)
        pred_class = np.argmax(preds, axis=1)[0]
        strategy = self.fnn_label_encoder.inverse_transform([pred_class])[0]
        return strategy