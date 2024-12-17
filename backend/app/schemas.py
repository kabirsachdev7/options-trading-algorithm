from typing import List, Optional
from pydantic import BaseModel

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

# Prediction Schemas
class PredictionRequest(BaseModel):
    ticker: str

class StrategyResponse(BaseModel):
    ticker: str
    predicted_close: float
    recommended_strategies: List[dict]

# Price Response
class PriceResponse(BaseModel):
    current_price: float

# Portfolio Schemas
class HoldingBase(BaseModel):
    ticker: str
    quantity: int
    purchase_price: float

class HoldingCreate(HoldingBase):
    pass

class Holding(HoldingBase):
    id: int

    class Config:
        orm_mode = True

class PortfolioBase(BaseModel):
    name: str

class PortfolioCreate(PortfolioBase):
    user_id: int

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    holdings: List[Holding] = []

    class Config:
        orm_mode = True

# Risk Metrics
class RiskMetrics(BaseModel):
    var: float  # Value at Risk
    sharpe_ratio: float
