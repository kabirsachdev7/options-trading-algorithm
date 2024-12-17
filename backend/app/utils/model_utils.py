from tensorflow.keras.models import load_model
import joblib
import os
import numpy as np
import pandas as pd

class ModelUtils:
    def __init__(self):
        self.lstm_model_path = os.path.join(os.path.dirname(__file__), '../../models/lstm_option_pricing.keras')
        self.fnn_model_path = os.path.join(os.path.dirname(__file__), '../../models/fnn_strategy.keras')
        self.fnn_scaler_path = os.path.join(os.path.dirname(__file__), '../../models/fnn_scaler.pkl')
        self.fnn_label_encoder_path = os.path.join(os.path.dirname(__file__), '../../models/fnn_label_encoder.pkl')
        
        self.lstm_model = self.load_lstm_model()
        self.fnn_model = self.load_fnn_model()
        self.fnn_scaler = self.load_fnn_scaler()
        self.fnn_label_encoder = self.load_fnn_label_encoder()
    
    def load_lstm_model(self):
        if not os.path.exists(self.lstm_model_path):
            raise FileNotFoundError(f"LSTM model not found at {self.lstm_model_path}")
        return load_model(self.lstm_model_path)
    
    def load_fnn_model(self):
        if not os.path.exists(self.fnn_model_path):
            raise FileNotFoundError(f"FNN model not found at {self.fnn_model_path}")
        return load_model(self.fnn_model_path)
    
    def load_fnn_scaler(self):
        if not os.path.exists(self.fnn_scaler_path):
            raise FileNotFoundError(f"FNN Scaler not found at {self.fnn_scaler_path}")
        return joblib.load(self.fnn_scaler_path)
    
    def load_fnn_label_encoder(self):
        if not os.path.exists(self.fnn_label_encoder_path):
            raise FileNotFoundError(f"FNN Label Encoder not found at {self.fnn_label_encoder_path}")
        return joblib.load(self.fnn_label_encoder_path)
    
    def predict_option_price(self, input_sequence):
        """
        input_sequence: numpy array of shape (1, TIME_STEPS, FEATURES)
        """
        prediction_scaled = self.lstm_model.predict(input_sequence)
        # Inverse transform if necessary
        # Assuming scaler was fitted with the first feature as 'Close'
        # Implement inverse transformation based on your scaler's configuration
        return float(prediction_scaled[0][0])
    
    def recommend_strategy(self, feature_data):
        """
        feature_data: numpy array with shape (1, FEATURES)
        """
        # Preprocess
        feature_data_scaled = self.fnn_scaler.transform(feature_data)
        
        # Predict
        predictions = self.fnn_model.predict(feature_data_scaled)
        predicted_class = np.argmax(predictions, axis=1)
        strategy = self.fnn_label_encoder.inverse_transform(predicted_class)
        return strategy[0]
