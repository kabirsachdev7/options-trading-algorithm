# backend/app/main.py

from fastapi import FastAPI, HTTPException, Depends, WebSocket
from dotenv import load_dotenv
import os
from app.auth import (
    get_current_user,
    authenticate_user,
    create_access_token,
    get_db,
    create_user
)
from app import schemas, models
from app.database import engine, Base
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocketDisconnect
from app.utils.connection_manager import ConnectionManager
from app.strategy import make_prediction, generate_strategies
from app.utils.model_utils import ModelUtils
from app.utils import data_fetcher
from app.utils.news_fetcher import fetch_top_business_news
import pandas as pd
import subprocess
import logging
from typing import List

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://frontend:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Connection Manager and Model Utils
manager = ConnectionManager()
model_utils = ModelUtils()

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        logging.warning(f"Registration attempt with existing username: {user.username}")
        raise HTTPException(status_code=400, detail="Username already taken.")
    new_user = create_user(db, user)
    logging.info(f"New user registered: {new_user.username}")
    return new_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logging.warning(f"Authentication failed for username: {form_data.username}")
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=None)
    logging.info(f"User logged in: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    logging.info(f"User info accessed: {current_user.username}")
    return current_user

@app.post("/predict", response_model=schemas.StrategyResponse)
def predict_endpoint(
    request: schemas.PredictionRequest,
    current_user: models.User = Depends(get_current_user)
):
    ticker = request.ticker.upper()
    logging.info(f"Predict request received for ticker: {ticker}")
    
    try:
        # Fetch historical price data with fallback
        price_data = data_fetcher.fetch_historical_data(ticker)
        data_source = price_data.get('data_source', 'Unknown')
        logging.info(f"Historical data fetched for {ticker} from {data_source}")
        
        # Fetch option chain from Yahoo Finance
        calls, puts, expiration_str = data_fetcher.fetch_option_chain(ticker)
        logging.info(f"Option chain data fetched for {ticker}, expiration: {expiration_str}")
        
        # Combine calls and puts
        calls['option_type'] = 'call'
        puts['option_type'] = 'put'
        options_data = pd.concat([calls, puts], ignore_index=True)
        
        # Process option data
        expiration_date = pd.to_datetime(expiration_str, utc=True, errors='coerce')
        if pd.isna(expiration_date):
            logging.error("Invalid expiration date from Yahoo Finance.")
            raise HTTPException(status_code=500, detail="Invalid expiration date from Yahoo Finance.")
        
        options_data['expiration'] = expiration_date
        current_price = price_data['Close'].iloc[-1]
        options_data['moneyness'] = (options_data['strike'] / current_price) - 1.0
        now = pd.Timestamp.now(tz='UTC')
        options_data['T'] = (options_data['expiration'] - now).dt.days / 365.0
        options_data.fillna(0, inplace=True)
        options_data['option_type_encoded'] = options_data['option_type'].map({'call': 1, 'put': 0})
        options_data['Close'] = current_price
        
        feature_cols = [
            'Close', 'strike', 'T', 'impliedVolatility', 'moneyness',
            'lastPrice', 'volume', 'openInterest', 'option_type_encoded'
        ]
        for col in feature_cols:
            if col not in options_data.columns:
                options_data[col] = 0.0
        
        # Attempt prediction
        try:
            predicted_close = make_prediction(ticker, options_data)
            logging.info(f"Prediction successful for {ticker}: {predicted_close}")
        except HTTPException as http_err:
            logging.error(f"HTTPException during prediction for {ticker}: {http_err.detail}")
            raise http_err
        except Exception as e:
            logging.error(f"Exception during prediction for {ticker}: {str(e)}")
            if "LSTM model not found" in str(e):
                # Train LSTM model
                logging.info(f"LSTM model for {ticker} not found. Initiating training...")
                try:
                    subprocess.run(["python", "backend/models/train_lstm_option_pricing.py", ticker], check=True)
                    logging.info(f"LSTM model trained successfully for {ticker}.")
                except subprocess.CalledProcessError as train_err:
                    logging.error(f"Failed to train LSTM model for {ticker}: {train_err}")
                    raise HTTPException(status_code=500, detail=f"Failed to train LSTM model for {ticker}.")
                
                # Retry prediction after training
                try:
                    predicted_close = make_prediction(ticker, options_data)
                    logging.info(f"Retry prediction successful for {ticker}: {predicted_close}")
                except Exception as second_try_err:
                    logging.error(f"Second attempt failed for {ticker}: {str(second_try_err)}")
                    raise HTTPException(status_code=500, detail=str(second_try_err))
            else:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Generate recommended strategies
        recommended_strategies = generate_strategies(ticker, predicted_close, options_data)
        logging.info(f"Recommended strategies generated for {ticker}: {recommended_strategies}")
        
        return {
            "ticker": ticker,
            "predicted_close": predicted_close,
            "recommended_strategies": recommended_strategies,
            "data_source": f"{data_source} (Price), Yahoo Finance (Options)"
        }
    
    except Exception as e:
        logging.error(f"Unhandled exception in predict_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@app.get("/price/{ticker}", response_model=schemas.PriceResponse)
def get_price(
    ticker: str,
    current_user: models.User = Depends(get_current_user)
):
    ticker = ticker.upper()
    logging.info(f"Price request received for ticker: {ticker}")
    try:
        price_data = data_fetcher.fetch_historical_data(ticker)
        current_price = price_data['Close'].iloc[-1]
        logging.info(f"Current price for {ticker}: {current_price}")
        return {"current_price": float(current_price)}
    except HTTPException as e:
        logging.error(f"Error fetching price for {ticker}: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unhandled exception fetching price for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@app.get("/portfolio", response_model=List[schemas.Holding])
def get_user_portfolio(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logging.info(f"Portfolio request received for user: {current_user.username}")
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == current_user.id).first()
    if not portfolio:
        logging.info(f"No portfolio found for user: {current_user.username}")
        return []
    
    holdings_data = []
    for holding in portfolio.holdings:
        ticker = holding.ticker.upper()
        logging.info(f"Fetching price for holding: {ticker}")
        try:
            price_data = data_fetcher.fetch_historical_data(ticker)
            current_price = price_data['Close'].iloc[-1]
            logging.info(f"Current price for {ticker}: {current_price}")
        except HTTPException as e:
            logging.warning(f"Could not fetch price for {ticker}: {e.detail}. Using purchase price.")
            current_price = holding.purchase_price
        except Exception as e:
            logging.error(f"Unhandled exception fetching price for {ticker}: {str(e)}. Using purchase price.")
            current_price = holding.purchase_price
        
        profit_loss = (current_price - holding.purchase_price) * holding.quantity
        holdings_data.append({
            "ticker": ticker,
            "quantity": holding.quantity,
            "purchase_price": holding.purchase_price,
            "current_price": float(current_price),
            "profit_loss": float(profit_loss)
        })
        logging.info(f"Holding updated: {ticker}, Profit/Loss: {profit_loss}")
    
    return holdings_data

@app.get("/news", response_model=List[schemas.NewsArticle])
def get_news(current_user: models.User = Depends(get_current_user)):
    logging.info(f"News request received for user: {current_user.username}")
    try:
        news = fetch_top_business_news()
        logging.info(f"Fetched {len(news)} news articles.")
        return news
    except HTTPException as e:
        logging.error(f"Error fetching news: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unhandled exception fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logging.info("WebSocket connected.")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info("WebSocket disconnected.")
