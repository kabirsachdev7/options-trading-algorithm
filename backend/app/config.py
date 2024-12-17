# backend/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    secret_key: str
    # other fields...

    class Config:
        env_file = "../.env"

settings = Settings()
