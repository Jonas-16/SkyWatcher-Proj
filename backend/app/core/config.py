from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Keys
    NASA_API_KEY: str = "DEMO_KEY"
    METEOMATICS_USERNAME: str = ""
    METEOMATICS_PASSWORD: str = ""
    GOOGLE_WEATHER_API_KEY: str = ""

    
    # Database
    DATABASE_URL: str = "sqlite:///./weather_app.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    # Allow all origins and explicitly add Codespaces backend URL
    ALLOWED_ORIGINS: List[str] = [
        "*",
        "https://shiny-waffle-pjqpg7v9p5vgf9rwj-8000.app.github.dev"
    ]
    
    # App Settings
    HISTORICAL_YEARS: int = 5
    DAYS_RANGE: int = 2
    
    class Config:
        env_file = ".env"

settings = Settings()
