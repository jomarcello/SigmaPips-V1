import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuratie uitschakelen
    MAIL_SERVER = None
    MAIL_PORT = None
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = None
    
    # Of helemaal verwijderen als je de email configuratie niet gebruikt 
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Service URLs
    TELEGRAM_SERVICE_URL = os.getenv("TELEGRAM_SERVICE_URL")
    
    # Scraping Settings
    NEWS_SOURCES = {
        "forexfactory": "https://www.forexfactory.com",
        "investing": "https://www.investing.com",
        "fxstreet": "https://www.fxstreet.com"
    }
    
    # Economic Calendar Settings
    CALENDAR_LOOKBACK_DAYS = 1
    CALENDAR_LOOKAHEAD_DAYS = 7
    
    # Analysis Settings
    NEWS_ITEMS_LIMIT = 10
    SENTIMENT_UPDATE_INTERVAL = 3600  # 1 hour in seconds 