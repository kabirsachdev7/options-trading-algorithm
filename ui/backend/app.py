# ui/backend/app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import os
import logging
import yfinance as yf
from typing import List

# Configure logging
logging.basicConfig(
    filename='/app/backend.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

app = FastAPI(title="Options Trading API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    tickers: List[str]  # Accept multiple tickers

class StrategyRecommendation(BaseModel):
    ticker: str
    recommended_contracts: List[dict]
    suggested_strategies: List[str]

class PredictionResponse(BaseModel):
    recommendations: List[StrategyRecommendation]

# Initialize scaler and model at startup
model_lstm = None
model_fnn = None
scaler = MinMaxScaler()
features = ['Close', 'strike', 'T', 'delta', 'gamma', 'theta', 'vega', 'rho', 'impliedVolatility']

@app.on_event("startup")
def load_resources():
    global model_lstm, model_fnn, scaler
    model_path_lstm = "/app/models/lstm_option_pricing.keras"
    model_path_fnn = "/app/models/fnn_option_pricing.keras"

    if not os.path.exists(model_path_lstm):
        logging.error(f"Model file {model_path_lstm} does not exist.")
        raise FileNotFoundError(f"Model file {model_path_lstm} does not exist.")
    if not os.path.exists(model_path_fnn):
        logging.error(f"Model file {model_path_fnn} does not exist.")
        raise FileNotFoundError(f"Model file {model_path_fnn} does not exist.")

    model_lstm = load_model(model_path_lstm)
    model_fnn = load_model(model_path_fnn)
    logging.info("Models loaded successfully.")

    # Load and fit scaler on a sample dataset or precomputed data
    # For simplicity, we'll assume a sample data file exists
    sample_data_path = "/app/data/merged_data_with_features_sample.csv"
    if not os.path.exists(sample_data_path):
        logging.error(f"Sample data file {sample_data_path} does not exist.")
        raise FileNotFoundError(f"Sample data file {sample_data_path} does not exist.")
    data = pd.read_csv(sample_data_path)
    scaler.fit(data[features])
    logging.info("Scaler fitted successfully.")

def fetch_real_time_data(ticker: str):
    # Fetch real-time stock data using yfinance
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="1m")  # 1 day data with 1-minute intervals
        return hist
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return None

def analyze_contracts(ticker: str):
    # Placeholder for fetching and analyzing options contracts
    # In practice, you'd use yfinance or another API to get options data
    try:
        stock = yf.Ticker(ticker)
        options_dates = stock.options
        contracts_info = []
        for date in options_dates:
            opt = stock.option_chain(date)
            calls = opt.calls.to_dict(orient='records')
            puts = opt.puts.to_dict(orient='records')
            contracts_info.extend([{'type': 'call', **call} for call in calls])
            contracts_info.extend([{'type': 'put', **put} for put in puts])
        return contracts_info
    except Exception as e:
        logging.error(f"Error fetching options contracts for {ticker}: {e}")
        return []

def recommend_strategies(ticker: str, contracts: List[dict]):
    # Analyze contracts using models to recommend strategies
    recommendations = []

    for contract in contracts:
        # Extract features required by models
        contract_features = [
            contract['lastPrice'],
            contract['strike'],
            contract['expiration'],  # Needs to be converted to 'T' (time to maturity)
            contract['delta'],
            contract['gamma'],
            contract['theta'],
            contract['vega'],
            contract['rho'],
            contract['impliedVolatility']
        ]

        # Preprocess features
        contract_features = scaler.transform([contract_features])
        contract_features = np.reshape(contract_features, (1, 1, len(features)))  # For LSTM
        
        # Predict using LSTM
        prediction_lstm = model_lstm.predict(contract_features)
        predicted_close_lstm = scaler.inverse_transform(
            np.concatenate((prediction_lstm, np.zeros((prediction_lstm.shape[0], scaler.n_features_in_ -1))), axis=1)
        )[0][0]

        # Predict using FNN
        contract_features_fnn = scaler.transform([contract_features.flatten()])
        prediction_fnn = model_fnn.predict(contract_features_fnn)
        predicted_close_fnn = scaler.inverse_transform(
            np.concatenate((prediction_fnn, np.zeros((prediction_fnn.shape[0], scaler.n_features_in_ -1))), axis=1)
        )[0][0]

        # Strategy Recommendation Logic (Simplified)
        if predicted_close_lstm > contract['strike']:
            strategy = "Buy Call"
        elif predicted_close_fnn < contract['strike']:
            strategy = "Sell Put"
        else:
            strategy = "Hold"

        recommendations.append({
            'contract': contract,
            'predicted_close_lstm': predicted_close_lstm,
            'predicted_close_fnn': predicted_close_fnn,
            'recommended_strategy': strategy
        })

    return recommendations

@app.post("/recommend-strategies", response_model=PredictionResponse)
def recommend_strategies_endpoint(request: PredictionRequest):
    recommendations = []
    for ticker in request.tickers:
        logging.info(f"Processing ticker: {ticker}")
        data = fetch_real_time_data(ticker)
        if data is None or data.empty:
            logging.warning(f"No data fetched for ticker: {ticker}")
            continue
        contracts = analyze_contracts(ticker)
        if not contracts:
            logging.warning(f"No contracts found for ticker: {ticker}")
            continue
        strategies = recommend_strategies(ticker, contracts)
        recommendations.append(StrategyRecommendation(
            ticker=ticker,
            recommended_contracts=[{
                'contract_type': s['contract']['type'],
                'strike': s['contract']['strike'],
                'expiration': s['contract']['expiration'],
                'strategy': s['recommended_strategy'],
                'predicted_close_lstm': s['predicted_close_lstm'],
                'predicted_close_fnn': s['predicted_close_fnn']
            } for s in strategies[:5]],  # Limiting to top 5 recommendations
            suggested_strategies=[s['recommended_strategy'] for s in strategies[:5]]
        ))
    return PredictionResponse(recommendations=recommendations)
