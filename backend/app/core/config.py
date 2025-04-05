from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Wildhacks2025"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB
    MONGO_URL: str = os.getenv("MONGO_URL")
    
    # Auth0
    AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN")
    AUTH0_API_AUDIENCE: str = os.getenv("AUTH0_API_AUDIENCE")
    AUTH0_ALGORITHMS: List[str] = ["RS256"]
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Session
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change this in production!

settings = Settings() 