# backend/app/main.py

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from app import models, schemas, database, auth, strategy
from app.utils.connection_manager import ConnectionManager
import os
import json
import asyncio
from app.config import settings

app = FastAPI(title="Options Trading API")

# CORS Configuration
origins = [
    "http://localhost:3000",  # Frontend URL
    # Add other allowed origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize Connection Manager
manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    await strategy.load_resources()
    asyncio.create_task(strategy.fetch_real_time_data(manager))

# ... [Other routes remain unchanged] ...

# Finnhub Webhook Endpoint
@app.post("/finnhub/webhook")
async def finnhub_webhook(request: Request, x_finnhub_secret: str = Header(None)):
    """
    Endpoint to receive Finnhub webhook events.
    """
    # Verify the secret
    if x_finnhub_secret != settings.finnhub_webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid secret.")
    
    # Acknowledge receipt immediately
    # It's crucial to return a 2xx status code before processing
    acknowledgment = {"status": "received"}
    asyncio.create_task(process_finnhub_event(request))
    return acknowledgment

async def process_finnhub_event(request: Request):
    """
    Process the Finnhub event asynchronously.
    """
    try:
        event = await request.json()
        # Implement your logic here based on the event data
        # For example, update database, trigger predictions, etc.
        print(f"Received Finnhub event: {event}")
        # Example: If the event contains ticker updates, fetch new data and retrain models if necessary
    except Exception as e:
        print(f"Error processing Finnhub event: {e}")
        # Optionally, implement retry mechanisms or logging
