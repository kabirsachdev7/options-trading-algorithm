import os

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///options_trading.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
API_KEY = os.getenv('API_KEY', 'your-api-key')
