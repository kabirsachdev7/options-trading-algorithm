# backend/app/auth.py
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import os

from app.database import SessionLocal
from app import models, schemas
from app.config import settings

# Secret key and algorithm from config
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user(db, username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Portfolio Management Functions
def create_portfolio(db: Session, portfolio: schemas.PortfolioCreate):
    db_portfolio = models.Portfolio(name=portfolio.name, user_id=portfolio.user_id)
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def get_portfolio(db: Session, user_id: int):
    return db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).first()

def add_holding(db: Session, user_id: int, holding: schemas.HoldingCreate):
    portfolio = get_portfolio(db, user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found.")
    db_holding = models.Holding(
        ticker=holding.ticker.upper(),
        quantity=holding.quantity,
        purchase_price=holding.purchase_price,
        portfolio_id=portfolio.id
    )
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)
    return db_holding

def remove_holding(db: Session, user_id: int, holding_id: int):
    portfolio = get_portfolio(db, user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found.")
    holding = db.query(models.Holding).filter(
        models.Holding.id == holding_id,
        models.Holding.portfolio_id == portfolio.id
    ).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found.")
    db.delete(holding)
    db.commit()
    return holding

def get_portfolio_risk(db: Session, user_id: int):
    portfolio = get_portfolio(db, user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found.")
    # Placeholder for risk calculations
    var = 1000.0  # Example Value at Risk
    sharpe_ratio = 1.5  # Example Sharpe Ratio
    return schemas.RiskMetrics(var=var, sharpe_ratio=sharpe_ratio)
