# backend/app/strategy.py

from fastapi import HTTPException
import numpy as np
from app.utils.model_utils import ModelUtils

model_utils = ModelUtils()

def get_execution_steps(strategy: str) -> str:
    if strategy == "call_spread":
        return "Buy an ITM call and sell an OTM call."
    elif strategy == "put_spread":
        return "Buy an ITM put and sell an OTM put."
    elif strategy == "iron_condor":
        return "Sell an OTM call spread and an OTM put spread simultaneously."
    elif strategy == "covered_call":
        return "Hold the underlying and sell a call option against it."
    elif strategy == "protective_put":
        return "Hold the underlying and buy a put option for downside protection."
    elif strategy == "straddle":
        return "Buy a call and a put at the same strike."
    elif strategy == "strangle":
        return "Buy a call and a put at different strikes, same expiration."
    elif strategy == "butterfly":
        return "Combine options at three different strike prices."
    else:
        return "Hold."

def make_prediction(ticker: str, data, time_steps=60):
    FEATURES = ['Close','strike','T','impliedVolatility','moneyness','lastPrice','volume','openInterest','option_type_encoded']
    if len(data) < time_steps:
        raise HTTPException(status_code=400, detail="Not enough data for prediction.")
    latest_data = data[FEATURES].tail(time_steps).values
    latest_data = np.reshape(latest_data, (1, time_steps, len(FEATURES)))
    try:
        predicted_close = model_utils.predict_option_price(ticker, latest_data)
    except ValueError as e:
        # Model not found or not trained
        raise HTTPException(status_code=500, detail=str(e))
    return predicted_close

def generate_strategies(ticker: str, predicted_close: float, data):
    latest_features = data.iloc[-1][['Close','strike','T','impliedVolatility','moneyness','lastPrice','volume','openInterest','option_type_encoded']].values.reshape(1,-1)
    strategy = model_utils.recommend_strategy(latest_features)
    return [{
        "name": strategy,
        "confidence": "High",
        "execution": get_execution_steps(strategy)
    }]
