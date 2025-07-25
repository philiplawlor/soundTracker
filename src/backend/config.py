"""
Configuration settings for the SoundTracker application.
"""
import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SoundTracker"
    
    # Audio capture settings
    AUDIO_DEVICE: Optional[int] = Field(
        default=int(os.getenv("AUDIO_DEVICE", "-1")),
        description="Audio device index (-1 means default device)"
    )
    AUDIO_SAMPLE_RATE: int = Field(
        default=int(os.getenv("AUDIO_SAMPLE_RATE", "44100")),
        description="Audio sample rate in Hz"
    )
    AUDIO_CHANNELS: int = Field(
        default=int(os.getenv("AUDIO_CHANNELS", "1")),
        description="Number of audio channels"
    )
    AUDIO_BLOCK_SIZE: int = Field(
        default=int(os.getenv("AUDIO_BLOCK_SIZE", "1024")),
        description="Audio block size for processing"
    )
    
    # WebSocket settings
    WEBSOCKET_UPDATE_INTERVAL: float = Field(
        default=float(os.getenv("WEBSOCKET_UPDATE_INTERVAL", "0.1")),
        description="WebSocket update interval in seconds"
    )
    
    # Database settings
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite:///./soundtracker.db"),
        description="Database connection URL"
    )
    
    # CORS settings
    CORS_ORIGINS: str = Field(
        default=os.getenv("CORS_ORIGINS", "*"),
        description="Comma-separated list of allowed CORS origins"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
settings = Settings()
