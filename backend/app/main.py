from fastapi import FastAPI, HTTPException, Depends, WebSocket
from dotenv import load_dotenv
import os
from app.auth import get_current_user, authenticate_user, create_access_token, get_db, create_user
from app import schemas, models
from app.database import engine, Base
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocketDisconnect
from app.utils.connection_manager import ConnectionManager
from app.strategy import make_prediction, generate_strategies
from app.utils.model_utils import ModelUtils
import yfinance as yf
import pandas as pd

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://frontend:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()
model_utils = ModelUtils()

@app.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken.")
    create_user(db, user)
    return {"message": "User registered successfully."}

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=None)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/predict")
def predict_endpoint(request: schemas.PredictionRequest, current_user: models.User = Depends(get_current_user)):
    ticker = request.ticker.upper()
    ticker_obj = yf.Ticker(ticker)
    price_data = ticker_obj.history(period="2y", interval='1d')
    if price_data.empty:
        raise HTTPException(status_code=404, detail="No price data for this ticker.")

    expirations = ticker_obj.options
    if not expirations:
        raise HTTPException(status_code=404, detail="No option chain available.")

    expiration_str = expirations[0]
    expiration_date = pd.to_datetime(expiration_str).tz_localize('UTC')
    chain = ticker_obj.option_chain(expiration_str)
    calls = chain.calls.copy()
    puts = chain.puts.copy()
    calls['option_type'] = 'call'
    puts['option_type'] = 'put'
    options_data = pd.concat([calls, puts], ignore_index=True)
    options_data['expiration'] = expiration_date

    # Engineer features as in training
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

    predicted_close = make_prediction(ticker, options_data)
    recommended_strategies = generate_strategies(ticker, predicted_close, options_data)

    return {
        "ticker": ticker,
        "predicted_close": predicted_close,
        "recommended_strategies": recommended_strategies,
    }

@app.get("/price/{ticker}")
def get_price(ticker: str, current_user: models.User = Depends(get_current_user)):
    ticker_obj = yf.Ticker(ticker)
    data = ticker_obj.history(period="1d")
    if data.empty:
        raise HTTPException(status_code=404, detail="Could not fetch price.")
    current_price = data['Close'].iloc[-1]
    return {"current_price": float(current_price)}

@app.get("/portfolio")
def get_user_portfolio(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == current_user.id).first()
    if not portfolio:
        return []
    holdings_data = []
    for h in portfolio.holdings:
        ticker_obj = yf.Ticker(h.ticker)
        data = ticker_obj.history(period="1d")
        if data.empty:
            current_price = h.purchase_price
        else:
            current_price = data['Close'].iloc[-1]
        profit_loss = (current_price - h.purchase_price) * h.quantity
        holdings_data.append({
            "ticker": h.ticker,
            "quantity": h.quantity,
            "purchase_price": h.purchase_price,
            "current_price": float(current_price),
            "profit_loss": float(profit_loss)
        })
    return holdings_data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
