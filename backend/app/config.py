# backend/app/config.py

from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    secret_key: str
    finnhub_api_key: str
    finnhub_webhook_secret: str

    class Config:
        env_file = "../.env"

settings = Settings()
