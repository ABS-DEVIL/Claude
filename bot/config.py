import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Config
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH")
    
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "abs_stream_fucker")
    
    # Web
    WEB_URL = os.getenv("WEB_URL", "http://localhost:8000")
    WEB_PORT = int(os.getenv("WEB_PORT", 8000))
    
    # Admin
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "abs_stream_fucker_secret")
    
    # Premium
    PREMIUM_USERS = [int(x) for x in os.getenv("PREMIUM_USERS", "").split(",") if x]
    
    # Storage
    STORAGE_PATH = os.getenv("STORAGE_PATH", "./downloads")
    
    # User Limits
    FREE_FILE_LIMIT = 4
    FREE_LINK_LIMIT = 5
    FREE_WAIT_TIME = 8
    FREE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds
    
    PREMIUM_WAIT_TIME = 0
    PREMIUM_EXPIRY = 365 * 24 * 60 * 60  # 1 year
    
    # Retry limits
    FREE_PASSWORD_RETRY = 3
    PREMIUM_PASSWORD_RETRY = 3
    
    # Bot personality
    BOT_NAME = "ABS_Stream_Fucker"
    
    # Supported leeching sites
    LEECH_SITES = [
        "terabox", "hubdrive", "hubcloud", 
        "gdflix", "filepress", "youtube.com", 
        "youtu.be", "instagram.com"
