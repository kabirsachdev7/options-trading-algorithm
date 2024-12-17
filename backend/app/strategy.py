# backend/app/strategy.py

from app.utils.model_utils import ModelUtils
from app.utils.finnhub_client import get_stock_quote, get_stock_profile
from app import schemas
import pandas as pd
import numpy as np
from fastapi import HTTPException
import os

# Initialize Model Utilities
model_utils = ModelUtils()

def make_prediction(ticker: str, data: pd.DataFrame):
    """
    Make a prediction for the given ticker using the LSTM model.
    """
    TIME_STEPS = 60
    FEATURES = ['Close', 'strike', 'T', 'delta', 'gamma', 'theta', 'vega', 'rho', 'impliedVolatility']
    
    if len(data) < TIME_STEPS:
        raise HTTPException(status_code=400, detail="Not enough data for prediction.")
    
    latest_data = data[FEATURES].tail(TIME_STEPS).values
    latest_data = np.reshape(latest_data, (1, TIME_STEPS, len(FEATURES)))
    
    predicted_close = model_utils.predict_option_price(latest_data)
    return predicted_close

def generate_strategies(ticker: str, predicted_close: float, data: pd.DataFrame) -> list:
    """
    Generate recommended options strategies based on the predicted close price
    using the FNN model.
    """
    latest_features = data.iloc[-1][['Close', 'strike', 'T', 'delta', 'gamma', 'theta', 'vega', 'rho', 'impliedVolatility']]
    
    # Reshape for model input
    feature_data = latest_features.values.reshape(1, -1)
    
    strategy = model_utils.recommend_strategy(feature_data)
    
    return [{
        "name": strategy,
        "confidence": "High",  # Placeholder: Implement confidence scoring if available
        "execution": get_execution_steps(strategy)
    }]
