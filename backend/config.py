"""
Configuration settings for the SoundTracker application.
"""
import os
from pydantic import BaseSettings, Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SoundTracker"
    
    # Audio capture settings
    AUDIO_DEVICE: Optional[int] = int(os.getenv("AUDIO_DEVICE", "-1"))  # -1 means default device
    AUDIO_SAMPLE_RATE: int = int(os.getenv("AUDIO_SAMPLE_RATE", "44100"))
    AUDIO_CHANNELS: int = int(os.getenv("AUDIO_CHANNELS", "1"))
    AUDIO_BLOCK_SIZE: int = int(os.getenv("AUDIO_BLOCK_SIZE", "1024"))
    
    # WebSocket settings
    WEBSOCKET_UPDATE_INTERVAL: float = float(os.getenv("WEBSOCKET_UPDATE_INTERVAL", "0.1"))
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./soundtracker.db")
    
    # CORS settings
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()
